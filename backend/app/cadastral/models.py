from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

try:
    from app.core.database import Base
except ImportError:
    try:
        from app.db.base import Base
    except ImportError:
        try:
            from app.database import Base
        except ImportError:
            from app.db import Base


class CadastralLayer(Base):
    __tablename__ = "cadastral_layers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    layer_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    source_format: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    crs: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    survey_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class OldParcel(Base):
    __tablename__ = "old_parcels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    layer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastral_layers.id", ondelete="CASCADE"),
        nullable=False,
    )

    parcel_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    geometry = mapped_column(
        Geometry(
            geometry_type="MULTIPOLYGON",
            srid=4326,
            spatial_index=True,
        ),
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    crs: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    area: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    perimeter: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class NewParcel(Base):
    __tablename__ = "new_parcels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    layer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastral_layers.id", ondelete="CASCADE"),
        nullable=False,
    )

    parcel_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    geometry = mapped_column(
        Geometry(
            geometry_type="MULTIPOLYGON",
            srid=4326,
            spatial_index=True,
        ),
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    crs: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    survey_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    area: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    perimeter: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class ParcelComparison(Base):
    __tablename__ = "parcel_comparisons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    old_parcel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("old_parcels.id", ondelete="SET NULL"),
        nullable=True,
    )

    new_parcel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("new_parcels.id", ondelete="SET NULL"),
        nullable=True,
    )

    old_area: Mapped[float | None] = mapped_column(Float)
    new_area: Mapped[float | None] = mapped_column(Float)

    area_difference: Mapped[float | None] = mapped_column(Float)
    area_change_percent: Mapped[float | None] = mapped_column(Float)

    old_perimeter: Mapped[float | None] = mapped_column(Float)
    new_perimeter: Mapped[float | None] = mapped_column(Float)
    perimeter_difference: Mapped[float | None] = mapped_column(Float)

    intersection_area: Mapped[float | None] = mapped_column(Float)
    union_area: Mapped[float | None] = mapped_column(Float)
    overlap_percent: Mapped[float | None] = mapped_column(Float)

    centroid_shift: Mapped[float | None] = mapped_column(Float)

    boundary_mean_difference: Mapped[float | None] = mapped_column(Float)
    boundary_max_difference: Mapped[float | None] = mapped_column(Float)

    change_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(Float)

    review_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    review_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
