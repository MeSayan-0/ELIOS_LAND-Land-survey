const API =
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000'

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API}${path}`,
    options,
  )

  if (!response.ok) {
    const text = await response.text()
    throw new Error(
      text || `HTTP ${response.status}`,
    )
  }

  return response.json()
}

export type GISLayer = {
  id: string
  name: string
  layer_type: string
  geometry_type: string
  crs: number
  survey_id?: string
  visible: boolean
  opacity: number
  style?: Record<string, unknown>
  fields?: Array<{
    name: string
    type: string
  }>
  feature_count: number
}

export type Raster = {
  id: string
  name: string
  public_url: string
  survey_id?: string
  crs?: number
  width?: number
  height?: number
  bands?: number
  resolution_x?: number
  resolution_y?: number
}

export async function getGISLayers(
  surveyId?: string,
) {
  const query = surveyId
    ? `?survey_id=${encodeURIComponent(surveyId)}`
    : ''

  return request<GISLayer[]>(
    `/api/gis/layers${query}`,
  )
}

export async function getRasterList(
  surveyId?: string,
) {
  const query = surveyId
    ? `?survey_id=${encodeURIComponent(surveyId)}`
    : ''

  return request<Raster[]>(
    `/api/gis/rasters${query}`,
  )
}

export async function createGISLayer(
  payload: Record<string, unknown>,
) {
  return request<GISLayer>(
    '/api/gis/layers',
    {
      method: 'POST',
      headers: {
        'Content-Type':
          'application/json',
      },
      body: JSON.stringify(payload),
    },
  )
}

export async function getLayerGeoJSON(
  layerId: string,
) {
  return request<any>(
    `/api/gis/layers/${layerId}/geojson`,
  )
}

export async function uploadOrthomosaic(
  file: File,
  surveyId?: string,
) {
  const form = new FormData()

  form.append('file', file)

  if (surveyId) {
    form.append(
      'survey_id',
      surveyId,
    )
  }

  return request<Raster>(
    '/api/gis/orthomosaic',
    {
      method: 'POST',
      body: form,
    },
  )
}

export async function importCSVPoints(
  file: File,
  options: {
    layerName: string
    layerType: string
    encoding: string
    delimiter: string
    xColumn: string
    yColumn: string
    crs: number
  },
) {
  const form = new FormData()

  form.append('file', file)
  form.append(
    'layer_name',
    options.layerName,
  )
  form.append(
    'layer_type',
    options.layerType,
  )
  form.append(
    'encoding',
    options.encoding,
  )
  form.append(
    'delimiter',
    options.delimiter,
  )
  form.append(
    'x_column',
    options.xColumn,
  )
  form.append(
    'y_column',
    options.yColumn,
  )
  form.append(
    'crs',
    String(options.crs),
  )

  return request(
    '/api/gis/points/import',
    {
      method: 'POST',
      body: form,
    },
  )
}

export async function importVector(
  file: File,
  options: {
    layerName: string
    layerType: string
    crsOverride?: number
  },
) {
  const form = new FormData()

  form.append('file', file)
  form.append(
    'layer_name',
    options.layerName,
  )
  form.append(
    'layer_type',
    options.layerType,
  )

  if (options.crsOverride) {
    form.append(
      'crs_override',
      String(options.crsOverride),
    )
  }

  return request(
    '/api/gis/vector/import',
    {
      method: 'POST',
      body: form,
    },
  )
}

export async function createFeature(
  payload: Record<string, unknown>,
) {
  return request<{ id: string }>(
    '/api/gis/features',
    {
      method: 'POST',
      headers: {
        'Content-Type':
          'application/json',
      },
      body: JSON.stringify(payload),
    },
  )
}

export async function updateFeature(
  featureId: string,
  payload: Record<string, unknown>,
) {
  return request(
    `/api/gis/features/${featureId}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type':
          'application/json',
      },
      body: JSON.stringify(payload),
    },
  )
}

export async function deleteFeature(
  featureId: string,
) {
  return request(
    `/api/gis/features/${featureId}`,
    {
      method: 'DELETE',
    },
  )
}

export async function updateLayerStyle(
  layerId: string,
  payload: Record<string, unknown>,
) {
  return request(
    `/api/gis/layers/${layerId}/style`,
    {
      method: 'POST',
      headers: {
        'Content-Type':
          'application/json',
      },
      body: JSON.stringify(payload),
    },
  )
}

export async function measureGeometry(
  geometry: unknown,
) {
  return request<{
    geometry_type: string
    area_m2: number
    perimeter_m: number
  }>(
    '/api/gis/measure',
    {
      method: 'POST',
      headers: {
        'Content-Type':
          'application/json',
      },
      body: JSON.stringify({
        geometry,
      }),
    },
  )
}

export async function calculateField(
  payload: Record<string, unknown>,
) {
  return request(
    '/api/gis/field-calculator',
    {
      method: 'POST',
      headers: {
        'Content-Type':
          'application/json',
      },
      body: JSON.stringify(payload),
    },
  )
}

export function exportLayerUrl(
  layerId: string,
  format: string,
) {
  return `${API}/api/gis/layers/${layerId}/export?format=${format}`
}
