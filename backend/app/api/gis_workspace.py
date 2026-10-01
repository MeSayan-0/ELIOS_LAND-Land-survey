from __future__ import annotations

import csv
import io
import json
import os
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import rasterio
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from shapely.geometry import (
    LineString,
    Point,
    Polygon,
    shape,
    mapping,
)
from shapely.ops import split, unary_union
from simpleeval import simple_eval
from psycopg import connect
from psycopg.rows import dict_row
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

router = APIRouter(prefix="/api/gis", tags=["GIS Workspace"])

GIS_STORAGE = BASE_DIR / "storage" / "gis"
RASTER_STORAGE = GIS_STORAGE / "rasters"
EXPORT_STORAGE = GIS_STORAGE / "exports"

RASTER_STORAGE.mkdir(parents=True, exist_ok=True)
EXPORT_STORAGE.mkdir(parents=True, exist_ok=True)


def db_url() -> str:
    value = (
        os.getenv("DATABASE_URL")
        or os.getenv("DATABASE_URI")
        or os.getenv("POSTGRES_URL")
    )

    if not value:
        raise RuntimeError("DATABASE_URL is not configured")

    return value.replace("+psycopg", "")


def conn():
    return connect(db_url(), row_factory=dict_row)


def clean_value(value: Any):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    return str(value)


def geojson_feature(feature_id, geom, properties):
    return {
        "type": "Feature",
        "id": str(feature_id),
        "geometry": mapping(geom),
        "properties": {
            **(properties or {}),
            "feature_id": str(feature_id),
        },
    }


@router.get("/health")
def gis_health():
    with conn() as db:
        with db.cursor() as cur:
            cur.execute("SELECT PostGIS_Version() AS version")
            row = cur.fetchone()

    return {
        "ok": True,
        "postgis": row["version"],
    }


@router.get("/layers")
def list_layers(
    survey_id: str | None = None,
):
    with conn() as db:
        with db.cursor() as cur:
            if survey_id:
                cur.execute("""
                    SELECT
                        id,
                        name,
                        layer_type,
                        geometry_type,
                        crs,
                        survey_id,
                        visible,
                        opacity,
                        style,
                        fields,
                        created_at,
                        updated_at,
                        (
                            SELECT COUNT(*)
                            FROM gis_features f
                            WHERE f.layer_id = l.id
                        ) AS feature_count
                    FROM gis_layers l
                    WHERE l.survey_id = %s
                    ORDER BY created_at
                """, (survey_id,))
            else:
                cur.execute("""
                    SELECT
                        id,
                        name,
                        layer_type,
                        geometry_type,
                        crs,
                        survey_id,
                        visible,
                        opacity,
                        style,
                        fields,
                        created_at,
                        updated_at,
                        (
                            SELECT COUNT(*)
                            FROM gis_features f
                            WHERE f.layer_id = l.id
                        ) AS feature_count
                    FROM gis_layers l
                    ORDER BY created_at
                """)

            return cur.fetchall()


@router.post("/layers")
def create_layer(payload: dict):
    layer_id = uuid.uuid4()

    name = str(payload.get("name", "")).strip()
    geometry_type = str(payload.get("geometry_type", "Polygon"))
    layer_type = str(payload.get("layer_type", "SURVEY_BOUNDARY"))
    crs = int(payload.get("crs", 4326))
    survey_id = payload.get("survey_id")

    if not name:
        raise HTTPException(400, "Layer name is required")

    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO gis_layers
                (
                    id,
                    name,
                    layer_type,
                    geometry_type,
                    crs,
                    survey_id,
                    style,
                    fields
                )
                VALUES
                (
                    %s,%s,%s,%s,%s,%s,%s,%s
                )
                """,
                (
                    layer_id,
                    name,
                    layer_type,
                    geometry_type,
                    crs,
                    survey_id,
                    json.dumps(payload.get("style", {})),
                    json.dumps(payload.get("fields", [])),
                ),
            )

    return {
        "id": str(layer_id),
        "name": name,
        "layer_type": layer_type,
        "geometry_type": geometry_type,
        "crs": crs,
    }


@router.get("/layers/{layer_id}/geojson")
def layer_geojson(layer_id: str):
    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    ST_AsGeoJSON(geom)::json AS geometry,
                    properties
                FROM gis_features
                WHERE layer_id = %s
                ORDER BY created_at
                """,
                (layer_id,),
            )

            rows = cur.fetchall()

    features = []

    for row in rows:
        features.append(
            {
                "type": "Feature",
                "id": str(row["id"]),
                "geometry": row["geometry"],
                "properties": {
                    **(row["properties"] or {}),
                    "feature_id": str(row["id"]),
                },
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


@router.post("/points/import")
async def import_points(
    file: UploadFile = File(...),
    layer_name: str = Form(...),
    layer_type: str = Form("RTK"),
    encoding: str = Form("utf-8"),
    delimiter: str = Form(";"),
    x_column: str = Form("Easting"),
    y_column: str = Form("Northing"),
    crs: int = Form(32633),
    survey_id: str | None = Form(None),
):
    raw = await file.read()

    try:
        text = raw.decode(encoding)
    except UnicodeDecodeError as exc:
        raise HTTPException(
            400,
            f"Unable to decode file with {encoding}",
        ) from exc

    df = pd.read_csv(
        io.StringIO(text),
        sep=delimiter,
    )

    if x_column not in df.columns:
        raise HTTPException(
            400,
            f"X column '{x_column}' not found. Available: {list(df.columns)}",
        )

    if y_column not in df.columns:
        raise HTTPException(
            400,
            f"Y column '{y_column}' not found. Available: {list(df.columns)}",
        )

    geometry = [
        Point(float(x), float(y))
        for x, y in zip(
            df[x_column],
            df[y_column],
        )
    ]

    gdf = gpd.GeoDataFrame(
        df,
        geometry=geometry,
        crs=f"EPSG:{crs}",
    )

    gdf = gdf.to_crs(4326)

    layer_id = uuid.uuid4()

    fields = [
        {
            "name": column,
            "type": str(df[column].dtype),
        }
        for column in df.columns
    ]

    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO gis_layers
                (
                    id,
                    name,
                    layer_type,
                    geometry_type,
                    crs,
                    survey_id,
                    fields
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    layer_id,
                    layer_name,
                    layer_type,
                    "Point",
                    crs,
                    survey_id,
                    json.dumps(fields),
                ),
            )

            for _, row in gdf.iterrows():
                feature_id = uuid.uuid4()

                properties = {
                    column: clean_value(row[column])
                    for column in df.columns
                }

                geom_json = json.dumps(
                    mapping(row.geometry)
                )

                cur.execute(
                    """
                    INSERT INTO gis_features
                    (
                        id,
                        layer_id,
                        geom,
                        properties,
                        source_crs
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        ST_SetSRID(ST_GeomFromGeoJSON(%s),4326),
                        %s,
                        %s
                    )
                    """,
                    (
                        feature_id,
                        layer_id,
                        geom_json,
                        json.dumps(properties),
                        crs,
                    ),
                )

    return {
        "layer_id": str(layer_id),
        "name": layer_name,
        "feature_count": len(gdf),
        "source_crs": crs,
        "stored_crs": 4326,
    }


@router.post("/vector/import")
async def import_vector(
    file: UploadFile = File(...),
    layer_name: str = Form(...),
    layer_type: str = Form("CADASTRAL"),
    crs_override: int | None = Form(None),
    survey_id: str | None = Form(None),
):
    suffix = Path(file.filename or "").suffix.lower()

    temp_dir = Path(
        tempfile.mkdtemp(
            prefix="helios_gis_"
        )
    )

    try:
        input_path = temp_dir / (file.filename or "input")

        with open(input_path, "wb") as handle:
            handle.write(await file.read())

        read_path = input_path

        if suffix == ".zip":
            extract_dir = temp_dir / "extracted"
            extract_dir.mkdir()

            with zipfile.ZipFile(input_path) as archive:
                archive.extractall(extract_dir)

            shp_files = list(
                extract_dir.rglob("*.shp")
            )

            if not shp_files:
                raise HTTPException(
                    400,
                    "ZIP does not contain a Shapefile",
                )

            read_path = shp_files[0]

        gdf = gpd.read_file(read_path)

        if gdf.empty:
            raise HTTPException(
                400,
                "Vector file contains no features",
            )

        if gdf.crs is None:
            if crs_override is None:
                raise HTTPException(
                    400,
                    "Input CRS is missing. Supply crs_override.",
                )

            gdf = gdf.set_crs(
                crs_override
            )

        source_crs = int(
            gdf.crs.to_epsg() or crs_override or 4326
        )

        gdf = gdf.to_crs(4326)

        geometry_types = {
            geom.geom_type
            for geom in gdf.geometry
            if geom is not None
        }

        if not geometry_types:
            raise HTTPException(
                400,
                "No valid geometry found",
            )

        geometry_type = sorted(
            geometry_types
        )[0]

        layer_id = uuid.uuid4()

        field_names = [
            column
            for column in gdf.columns
            if column != "geometry"
        ]

        fields = [
            {
                "name": column,
                "type": str(
                    gdf[column].dtype
                ),
            }
            for column in field_names
        ]

        with conn() as db:
            with db.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO gis_layers
                    (
                        id,
                        name,
                        layer_type,
                        geometry_type,
                        crs,
                        survey_id,
                        fields
                    )
                    VALUES
                    (%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        layer_id,
                        layer_name,
                        layer_type,
                        geometry_type,
                        source_crs,
                        survey_id,
                        json.dumps(fields),
                    ),
                )

                for _, row in gdf.iterrows():
                    if row.geometry is None:
                        continue

                    feature_id = uuid.uuid4()

                    properties = {
                        column: clean_value(
                            row[column]
                        )
                        for column in field_names
                    }

                    cur.execute(
                        """
                        INSERT INTO gis_features
                        (
                            id,
                            layer_id,
                            geom,
                            properties,
                            source_crs
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            ST_SetSRID(
                                ST_GeomFromGeoJSON(%s),
                                4326
                            ),
                            %s,
                            %s
                        )
                        """,
                        (
                            feature_id,
                            layer_id,
                            json.dumps(
                                mapping(
                                    row.geometry
                                )
                            ),
                            json.dumps(properties),
                            source_crs,
                        ),
                    )

        return {
            "layer_id": str(layer_id),
            "name": layer_name,
            "feature_count": len(gdf),
            "source_crs": source_crs,
            "stored_crs": 4326,
        }

    finally:
        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )


@router.post("/features")
def create_feature(payload: dict):
    layer_id = payload.get("layer_id")
    geometry = payload.get("geometry")
    properties = payload.get("properties", {})

    if not layer_id or not geometry:
        raise HTTPException(
            400,
            "layer_id and geometry are required",
        )

    feature_id = uuid.uuid4()

    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO gis_features
                (
                    id,
                    layer_id,
                    geom,
                    properties
                )
                VALUES
                (
                    %s,
                    %s,
                    ST_SetSRID(
                        ST_GeomFromGeoJSON(%s),
                        4326
                    ),
                    %s
                )
                """,
                (
                    feature_id,
                    layer_id,
                    json.dumps(geometry),
                    json.dumps(properties),
                ),
            )

    return {
        "id": str(feature_id),
    }


@router.put("/features/{feature_id}")
def update_feature(
    feature_id: str,
    payload: dict,
):
    geometry = payload.get("geometry")
    properties = payload.get("properties", {})

    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                UPDATE gis_features
                SET
                    geom = ST_SetSRID(
                        ST_GeomFromGeoJSON(%s),
                        4326
                    ),
                    properties = %s,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id
                """,
                (
                    json.dumps(geometry),
                    json.dumps(properties),
                    feature_id,
                ),
            )

            row = cur.fetchone()

    if not row:
        raise HTTPException(
            404,
            "Feature not found",
        )

    return {
        "id": str(row["id"]),
        "updated": True,
    }


@router.delete("/features/{feature_id}")
def delete_feature(feature_id: str):
    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                DELETE FROM gis_features
                WHERE id = %s
                RETURNING id
                """,
                (feature_id,),
            )

            row = cur.fetchone()

    if not row:
        raise HTTPException(
            404,
            "Feature not found",
        )

    return {
        "deleted": True,
    }


@router.post("/layers/{layer_id}/style")
def update_layer_style(
    layer_id: str,
    payload: dict,
):
    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                UPDATE gis_layers
                SET
                    visible = COALESCE(
                        %s,
                        visible
                    ),
                    opacity = COALESCE(
                        %s,
                        opacity
                    ),
                    style = COALESCE(
                        %s,
                        style
                    ),
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id
                """,
                (
                    payload.get("visible"),
                    payload.get("opacity"),
                    json.dumps(
                        payload["style"]
                    )
                    if "style" in payload
                    else None,
                    layer_id,
                ),
            )

            row = cur.fetchone()

    if not row:
        raise HTTPException(
            404,
            "Layer not found",
        )

    return {
        "updated": True,
    }


@router.post("/measure")
def measure(payload: dict):
    geometry = payload.get("geometry")

    if not geometry:
        raise HTTPException(
            400,
            "geometry is required",
        )

    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT
                    ST_GeometryType(
                        ST_SetSRID(
                            ST_GeomFromGeoJSON(%s),
                            4326
                        )
                    ) AS geometry_type,
                    ST_Area(
                        ST_SetSRID(
                            ST_GeomFromGeoJSON(%s),
                            4326
                        )::geography
                    ) AS area_m2,
                    ST_Perimeter(
                        ST_SetSRID(
                            ST_GeomFromGeoJSON(%s),
                            4326
                        )::geography
                    ) AS perimeter_m
                """,
                (
                    json.dumps(geometry),
                    json.dumps(geometry),
                    json.dumps(geometry),
                ),
            )

            row = cur.fetchone()

    return {
        "geometry_type": row["geometry_type"],
        "area_m2": float(row["area_m2"] or 0),
        "perimeter_m": float(
            row["perimeter_m"] or 0
        ),
    }


@router.post("/field-calculator")
def field_calculator(payload: dict):
    layer_id = payload.get("layer_id")
    field = str(payload.get("field", "")).strip()
    expression = str(
        payload.get("expression", "")
    ).strip()

    feature_ids = payload.get("feature_ids")

    if not layer_id or not field or not expression:
        raise HTTPException(
            400,
            "layer_id, field and expression are required",
        )

    if "__" in expression:
        raise HTTPException(
            400,
            "Unsafe expression",
        )

    with conn() as db:
        with db.cursor() as cur:
            if feature_ids:
                cur.execute(
                    """
                    SELECT
                        id,
                        properties
                    FROM gis_features
                    WHERE layer_id = %s
                    AND id = ANY(%s::uuid[])
                    """,
                    (
                        layer_id,
                        feature_ids,
                    ),
                )
            else:
                cur.execute(
                    """
                    SELECT
                        id,
                        properties
                    FROM gis_features
                    WHERE layer_id = %s
                    """,
                    (layer_id,),
                )

            rows = cur.fetchall()

            changed = 0

            for row in rows:
                properties = row["properties"] or {}

                names = {
                    key: value
                    for key, value
                    in properties.items()
                    if isinstance(
                        value,
                        (int, float, str)
                    )
                }

                names.update(
                    {
                        "pi": 3.141592653589793,
                    }
                )

                try:
                    result = simple_eval(
                        expression,
                        names=names,
                        functions={
                            "round": round,
                            "abs": abs,
                            "min": min,
                            "max": max,
                            "str": str,
                        },
                    )
                except Exception as exc:
                    raise HTTPException(
                        400,
                        f"Expression failed: {exc}",
                    ) from exc

                properties[field] = result

                cur.execute(
                    """
                    UPDATE gis_features
                    SET
                        properties = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (
                        json.dumps(properties),
                        row["id"],
                    ),
                )

                changed += 1

    return {
        "updated_features": changed,
        "field": field,
    }


@router.post("/merge")
def merge_features(payload: dict):
    feature_ids = payload.get("feature_ids", [])

    if len(feature_ids) < 2:
        raise HTTPException(
            400,
            "Select at least two features",
        )

    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    layer_id,
                    ST_AsGeoJSON(geom)::json AS geometry
                FROM gis_features
                WHERE id = ANY(%s::uuid[])
                """,
                (feature_ids,),
            )

            rows = cur.fetchall()

            if len(rows) < 2:
                raise HTTPException(
                    404,
                    "Features not found",
                )

            layer_id = rows[0]["layer_id"]

            geometries = [
                shape(row["geometry"])
                for row in rows
            ]

            merged = unary_union(geometries)

            new_id = uuid.uuid4()

            cur.execute(
                """
                INSERT INTO gis_features
                (
                    id,
                    layer_id,
                    geom,
                    properties
                )
                VALUES
                (
                    %s,
                    %s,
                    ST_SetSRID(
                        ST_GeomFromGeoJSON(%s),
                        4326
                    ),
                    %s
                )
                """,
                (
                    new_id,
                    layer_id,
                    json.dumps(mapping(merged)),
                    json.dumps(
                        {
                            "merged_from":
                                feature_ids
                        }
                    ),
                ),
            )

            cur.execute(
                """
                DELETE FROM gis_features
                WHERE id = ANY(%s::uuid[])
                """,
                (feature_ids,),
            )

    return {
        "new_feature_id": str(new_id),
        "merged_count": len(feature_ids),
    }


@router.post("/split/{feature_id}")
def split_feature(
    feature_id: str,
    payload: dict,
):
    line_geometry = payload.get("line")

    if not line_geometry:
        raise HTTPException(
            400,
            "line is required",
        )

    cutter = shape(line_geometry)

    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT
                    layer_id,
                    ST_AsGeoJSON(geom)::json AS geometry,
                    properties
                FROM gis_features
                WHERE id = %s
                """,
                (feature_id,),
            )

            row = cur.fetchone()

            if not row:
                raise HTTPException(
                    404,
                    "Feature not found",
                )

            polygon = shape(
                row["geometry"]
            )

            pieces = split(
                polygon,
                cutter,
            )

            if len(pieces.geoms) < 2:
                raise HTTPException(
                    400,
                    "Split line did not divide the polygon",
                )

            new_ids = []

            for piece in pieces.geoms:
                new_id = uuid.uuid4()

                cur.execute(
                    """
                    INSERT INTO gis_features
                    (
                        id,
                        layer_id,
                        geom,
                        properties
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        ST_SetSRID(
                            ST_GeomFromGeoJSON(%s),
                            4326
                        ),
                        %s
                    )
                    """,
                    (
                        new_id,
                        row["layer_id"],
                        json.dumps(
                            mapping(piece)
                        ),
                        json.dumps(
                            row["properties"] or {}
                        ),
                    ),
                )

                new_ids.append(
                    str(new_id)
                )

            cur.execute(
                """
                DELETE FROM gis_features
                WHERE id = %s
                """,
                (feature_id,),
            )

    return {
        "new_feature_ids": new_ids,
    }


@router.post("/orthomosaic")
async def upload_orthomosaic(
    file: UploadFile = File(...),
    survey_id: str | None = Form(None),
):
    filename = file.filename or "orthomosaic.tif"

    if not filename.lower().endswith(
        (".tif", ".tiff")
    ):
        raise HTTPException(
            400,
            "Only GeoTIFF files are supported",
        )

    raster_id = uuid.uuid4()

    safe_name = (
        f"{raster_id}_{Path(filename).name}"
    )

    output_path = (
        RASTER_STORAGE / safe_name
    )

    with open(output_path, "wb") as handle:
        shutil.copyfileobj(
            file.file,
            handle,
        )

    try:
        with rasterio.open(output_path) as src:
            crs = (
                src.crs.to_epsg()
                if src.crs
                else None
            )

            bounds = src.bounds

            width = src.width
            height = src.height
            bands = src.count

            resolution_x = src.res[0]
            resolution_y = src.res[1]

    except Exception as exc:
        output_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            400,
            f"Unable to read GeoTIFF: {exc}",
        ) from exc

    public_url = (
        f"/api/gis/rasters/{raster_id}"
    )

    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO gis_rasters
                (
                    id,
                    name,
                    file_path,
                    public_url,
                    survey_id,
                    crs,
                    width,
                    height,
                    bands,
                    resolution_x,
                    resolution_y,
                    min_x,
                    min_y,
                    max_x,
                    max_y
                )
                VALUES
                (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s
                )
                """,
                (
                    raster_id,
                    filename,
                    str(output_path),
                    public_url,
                    survey_id,
                    crs,
                    width,
                    height,
                    bands,
                    resolution_x,
                    resolution_y,
                    bounds.left,
                    bounds.bottom,
                    bounds.right,
                    bounds.top,
                ),
            )

    return {
        "id": str(raster_id),
        "name": filename,
        "url": public_url,
        "crs": crs,
        "width": width,
        "height": height,
        "bands": bands,
        "resolution": [
            resolution_x,
            resolution_y,
        ],
    }


@router.get("/rasters")
def list_rasters(
    survey_id: str | None = None,
):
    with conn() as db:
        with db.cursor() as cur:
            if survey_id:
                cur.execute(
                    """
                    SELECT
                        id,
                        name,
                        public_url,
                        survey_id,
                        crs,
                        width,
                        height,
                        bands,
                        resolution_x,
                        resolution_y,
                        min_x,
                        min_y,
                        max_x,
                        max_y,
                        created_at
                    FROM gis_rasters
                    WHERE survey_id = %s
                    ORDER BY created_at DESC
                    """,
                    (survey_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT
                        id,
                        name,
                        public_url,
                        survey_id,
                        crs,
                        width,
                        height,
                        bands,
                        resolution_x,
                        resolution_y,
                        min_x,
                        min_y,
                        max_x,
                        max_y,
                        created_at
                    FROM gis_rasters
                    ORDER BY created_at DESC
                    """
                )

            return cur.fetchall()


@router.get("/rasters/{raster_id}")
def get_raster(raster_id: str):
    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM gis_rasters
                WHERE id = %s
                """,
                (raster_id,),
            )

            row = cur.fetchone()

    if not row:
        raise HTTPException(
            404,
            "Raster not found",
        )

    return FileResponse(
        row["file_path"],
        media_type="image/tiff",
        filename=row["name"],
    )


@router.get("/layers/{layer_id}/export")
def export_layer(
    layer_id: str,
    format: str = "geojson",
):
    format = format.lower()

    with conn() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT
                    l.name,
                    l.crs,
                    f.id,
                    f.properties,
                    ST_AsGeoJSON(f.geom)::json AS geometry
                FROM gis_layers l
                JOIN gis_features f
                    ON f.layer_id = l.id
                WHERE l.id = %s
                ORDER BY f.created_at
                """,
                (layer_id,),
            )

            rows = cur.fetchall()

    if not rows:
        raise HTTPException(
            404,
            "Layer has no features",
        )

    layer_name = rows[0]["name"]

    features = [
        {
            "type": "Feature",
            "id": str(row["id"]),
            "geometry": row["geometry"],
            "properties": row["properties"] or {},
        }
        for row in rows
    ]

    if format == "geojson":
        path = (
            EXPORT_STORAGE
            / f"{layer_name}.geojson"
        )

        path.write_text(
            json.dumps(
                {
                    "type": "FeatureCollection",
                    "features": features,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        return FileResponse(
            path,
            media_type="application/geo+json",
            filename=path.name,
        )

    if format == "csv":
        path = (
            EXPORT_STORAGE
            / f"{layer_name}.csv"
        )

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8",
        ) as handle:
            writer = csv.writer(handle)

            property_keys = sorted(
                {
                    key
                    for feature in features
                    for key in feature[
                        "properties"
                    ].keys()
                }
            )

            writer.writerow(
                [
                    *property_keys,
                    "geometry_wkt",
                ]
            )

            for feature in features:
                geom = shape(
                    feature["geometry"]
                )

                writer.writerow(
                    [
                        feature["properties"].get(
                            key
                        )
                        for key in property_keys
                    ]
                    + [geom.wkt]
                )

        return FileResponse(
            path,
            media_type="text/csv",
            filename=path.name,
        )

    if format not in {
        "shp",
        "gpkg",
        "kml",
    }:
        raise HTTPException(
            400,
            "Supported exports: geojson, csv, shp, gpkg, kml",
        )

    gdf = gpd.GeoDataFrame.from_features(
        features,
        crs="EPSG:4326",
    )

    if format == "gpkg":
        path = (
            EXPORT_STORAGE
            / f"{layer_name}.gpkg"
        )

        gdf.to_file(
            path,
            layer="features",
            driver="GPKG",
        )

        return FileResponse(
            path,
            media_type="application/geopackage+sqlite3",
            filename=path.name,
        )

    if format == "kml":
        path = (
            EXPORT_STORAGE
            / f"{layer_name}.kml"
        )

        gdf.to_file(
            path,
            driver="KML",
        )

        return FileResponse(
            path,
            media_type="application/vnd.google-earth.kml+xml",
            filename=path.name,
        )

    folder = (
        EXPORT_STORAGE / layer_name
    )

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    shp_path = (
        folder / f"{layer_name}.shp"
    )

    gdf.to_file(
        shp_path,
        driver="ESRI Shapefile",
    )

    zip_path = (
        EXPORT_STORAGE
        / f"{layer_name}.zip"
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as archive:
        for item in folder.iterdir():
            archive.write(
                item,
                item.name,
            )

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=zip_path.name,
    )
