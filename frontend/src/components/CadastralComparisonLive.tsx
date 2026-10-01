import {
  useEffect,
  useMemo,
  useState,
} from 'react'

type Layer = {
  id: string
  name: string
  layer_type: 'OLD' | 'NEW'
  parcel_count: number
  crs?: string
  source?: string
}

type Comparison = {
  id: string
  old_parcel_code?: string
  new_parcel_code?: string
  old_area?: number
  new_area?: number
  area_difference?: number
  area_change_percent?: number
  old_perimeter?: number
  new_perimeter?: number
  perimeter_difference?: number
  intersection_area?: number
  union_area?: number
  overlap_percent?: number
  centroid_shift?: number
  boundary_mean_difference?: number
  boundary_max_difference?: number
  change_type: string
  confidence?: number
}

type RunResult = {
  run_id: string
  summary: Record<string, number>
  comparisons: Comparison[]
  projected_crs?: string
}

type GeoFeature = {
  type: string
  geometry: any
  properties: any
}

type GeoJSONResult = {
  type: string
  features: GeoFeature[]
}

const API =
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000'

async function request(
  path: string,
  options?: RequestInit,
) {
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

function collectCoordinates(
  geometry: any,
): number[][] {
  if (!geometry) return []

  if (
    geometry.type === 'Point'
  ) {
    return [geometry.coordinates]
  }

  if (
    geometry.type === 'LineString'
  ) {
    return geometry.coordinates
  }

  if (
    geometry.type === 'Polygon'
  ) {
    return geometry.coordinates.flat()
  }

  if (
    geometry.type === 'MultiPolygon'
  ) {
    return geometry.coordinates.flat(2)
  }

  return []
}

function geometryPath(
  geometry: any,
  project: (p: number[]) => string,
) {
  if (!geometry) return ''

  const ringPath = (
    ring: number[][],
  ) =>
    ring
      .map(
        (p, index) =>
          `${index === 0 ? 'M' : 'L'} ${project(p)}`,
      )
      .join(' ') + ' Z'

  if (
    geometry.type === 'Polygon'
  ) {
    return geometry.coordinates
      .map(ringPath)
      .join(' ')
  }

  if (
    geometry.type === 'MultiPolygon'
  ) {
    return geometry.coordinates
      .flatMap(
        (polygon: number[][][]) =>
          polygon.map(ringPath),
      )
      .join(' ')
  }

  return ''
}

function formatArea(
  value?: number,
) {
  if (value == null) return '—'
  return `${value.toLocaleString(undefined, {
    maximumFractionDigits: 2,
  })} m²`
}

function formatMeters(
  value?: number,
) {
  if (value == null) return '—'
  return `${value.toLocaleString(undefined, {
    maximumFractionDigits: 2,
  })} m`
}

function formatPercent(
  value?: number,
) {
  if (value == null) return '—'
  return `${value.toFixed(2)}%`
}

export default function CadastralComparisonLive() {
  const [
    layers,
    setLayers,
  ] = useState<Layer[]>([])

  const [
    oldLayer,
    setOldLayer,
  ] = useState('')

  const [
    newLayer,
    setNewLayer,
  ] = useState('')

  const [
    run,
    setRun,
  ] = useState<RunResult | null>(null)

  const [
    geojson,
    setGeojson,
  ] = useState<GeoJSONResult | null>(
    null,
  )

  const [
    selected,
    setSelected,
  ] = useState<Comparison | null>(
    null,
  )

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    message,
    setMessage,
  ] = useState('')

  const [
    error,
    setError,
  ] = useState('')

  const loadLayers = async () => {
    try {
      const result =
        await request(
          '/api/cadastral/layers',
        )

      setLayers(
        result.layers || [],
      )
    } catch (err: any) {
      setError(
        err.message ||
          'Could not load cadastral layers.',
      )
    }
  }

  useEffect(() => {
    loadLayers()
  }, [])

  const oldLayers = layers.filter(
    x => x.layer_type === 'OLD',
  )

  const newLayers = layers.filter(
    x => x.layer_type === 'NEW',
  )

  // The backend comparison summary may not always expose the
  // NEW parcel count correctly. The layer itself is authoritative
  // for the number of imported new parcels.
  const selectedOldLayer =
    oldLayers.find(
      layer => layer.id === oldLayer,
    )

  const selectedNewLayer =
    newLayers.find(
      layer => layer.id === newLayer,
    )

  const importLayer = async (
    type: 'OLD' | 'NEW',
    file: File,
  ) => {
    setLoading(true)
    setError('')
    setMessage('Importing cadastral data...')

    try {
      const form =
        new FormData()

      form.append(
        'file',
        file,
      )

      form.append(
        'layer_type',
        type,
      )

      form.append(
        'name',
        file.name,
      )

      const response =
        await fetch(
          `${API}/api/cadastral/import`,
          {
            method: 'POST',
            body: form,
          },
        )

      if (!response.ok) {
        throw new Error(
          await response.text(),
        )
      }

      const result =
        await response.json()

      setMessage(
        `${type} cadastre imported: ${result.parcel_count} parcels.`,
      )

      await loadLayers()

      if (type === 'OLD') {
        setOldLayer(
          result.layer_id,
        )
      } else {
        setNewLayer(
          result.layer_id,
        )
      }
    } catch (err: any) {
      setError(
        err.message ||
          'Import failed.',
      )
    } finally {
      setLoading(false)
    }
  }

  const executeComparison =
    async () => {
      if (
        !oldLayer ||
        !newLayer
      ) {
        setError(
          'Select both an old and a new cadastral layer.',
        )
        return
      }

      setLoading(true)
      setError('')
      setMessage(
        'Running cadastral comparison...',
      )

      try {
        const result =
          await request(
            '/api/cadastral/compare',
            {
              method: 'POST',
              headers: {
                'Content-Type':
                  'application/json',
              },
              body: JSON.stringify({
                old_layer_id:
                  oldLayer,
                new_layer_id:
                  newLayer,
              }),
            },
          )

        setRun(result)

        const map =
          await request(
            `/api/cadastral/comparison/${result.run_id}/geojson`,
          )

        setGeojson(map)

        setSelected(null)

        setMessage(
          'Cadastral comparison completed.',
        )
      } catch (err: any) {
        setError(
          err.message ||
            'Comparison failed.',
        )
      } finally {
        setLoading(false)
      }
    }

  const mapBounds =
    useMemo(() => {
      const coordinates =
        geojson?.features.flatMap(
          feature =>
            collectCoordinates(
              feature.geometry,
            ),
        ) || []

      if (!coordinates.length)
        return null

      const xs =
        coordinates.map(
          p => p[0],
        )

      const ys =
        coordinates.map(
          p => p[1],
        )

      return {
        minX: Math.min(...xs),
        maxX: Math.max(...xs),
        minY: Math.min(...ys),
        maxY: Math.max(...ys),
      }
    }, [geojson])

  const project =
    (point: number[]) => {
      if (!mapBounds)
        return '0,0'

      const width = 880
      const height = 500
      const pad = 35

      const dx =
        mapBounds.maxX -
        mapBounds.minX ||
        1

      const dy =
        mapBounds.maxY -
        mapBounds.minY ||
        1

      const scale =
        Math.min(
          (width - pad * 2) /
            dx,
          (height - pad * 2) /
            dy,
        )

      const x =
        pad +
        (point[0] -
          mapBounds.minX) *
          scale

      const y =
        height -
        pad -
        (point[1] -
          mapBounds.minY) *
          scale

      return `${x.toFixed(2)},${y.toFixed(2)}`
    }

  const selectedComparison =
    selected

  const summary =
    run?.summary

  const openReport =
    () => {
      if (!run) return

      window.open(
        `${API}/api/cadastral/report/${run.run_id}`,
        '_blank',
      )
    }

  const createVerification =
    async () => {
      if (
        !run ||
        !selectedComparison
      )
        return

      try {
        const result =
          await request(
            `/api/cadastral/comparison/${run.run_id}/verification`,
            {
              method: 'POST',
              headers: {
                'Content-Type':
                  'application/json',
              },
              body: JSON.stringify({
                comparison_id:
                  selectedComparison.id,
                officer_name:
                  'Survey Operator',
              }),
            },
          )

        setMessage(
          `Verification case created: ${result.case_id}`,
        )
      } catch (err: any) {
        setError(
          err.message ||
            'Could not create verification case.',
        )
      }
    }

  return (
    <div
      style={{
        display: 'grid',
        gap: 18,
      }}
    >
      <div>
        <div
          style={{
            fontSize: 10,
            letterSpacing: 2,
            color: '#58a6ff',
            fontWeight: 700,
            marginBottom: 7,
          }}
        >
          GEOMETRY ANALYSIS
        </div>

        <h1
          style={{
            margin: 0,
            fontSize: 26,
            color: '#f4f7fb',
          }}
        >
          Cadastral comparison
        </h1>

        <p
          style={{
            marginTop: 7,
            color: '#8c9aaa',
            fontSize: 13,
          }}
        >
          Compare recorded cadastral
          geometry against the new
          survey boundary using spatial
          analysis.
        </p>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            '1fr 1fr auto',
          gap: 10,
          padding: 14,
          border:
            '1px solid #223246',
          borderRadius: 8,
          background:
            '#0c1723',
        }}
      >
        <select
          value={oldLayer}
          onChange={e =>
            setOldLayer(
              e.target.value,
            )
          }
          style={{
            padding: 11,
            background: '#09131e',
            color: '#dbe6f2',
            border:
              '1px solid #2a3b4f',
            borderRadius: 6,
          }}
        >
          <option value="">
            Select old cadastre
          </option>

          {oldLayers.map(
            layer => (
              <option
                key={layer.id}
                value={layer.id}
              >
                {layer.name} ·{' '}
                {layer.parcel_count}{' '}
                parcels
              </option>
            ),
          )}
        </select>

        <select
          value={newLayer}
          onChange={e =>
            setNewLayer(
              e.target.value,
            )
          }
          style={{
            padding: 11,
            background: '#09131e',
            color: '#dbe6f2',
            border:
              '1px solid #2a3b4f',
            borderRadius: 6,
          }}
        >
          <option value="">
            Select new cadastre
          </option>

          {newLayers.map(
            layer => (
              <option
                key={layer.id}
                value={layer.id}
              >
                {layer.name} ·{' '}
                {layer.parcel_count}{' '}
                parcels
              </option>
            ),
          )}
        </select>

        <button
          onClick={
            executeComparison
          }
          disabled={loading}
          style={{
            border: 0,
            borderRadius: 6,
            padding:
              '0 18px',
            background:
              '#2678ff',
            color: 'white',
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          {loading
            ? 'Processing...'
            : 'Run comparison'}
        </button>
      </div>

      <div
        style={{
          display: 'flex',
          gap: 10,
        }}
      >
        <label
          style={{
            padding:
              '9px 13px',
            border:
              '1px solid #2a3b4f',
            borderRadius: 6,
            cursor: 'pointer',
            color: '#b9c8d8',
          }}
        >
          Import old cadastre
          <input
            type="file"
            accept=".geojson,.json,.gpkg,.zip,.shp"
            hidden
            onChange={e => {
              const file =
                e.target.files?.[0]

              if (file)
                importLayer(
                  'OLD',
                  file,
                )
            }}
          />
        </label>

        <label
          style={{
            padding:
              '9px 13px',
            border:
              '1px solid #2a3b4f',
            borderRadius: 6,
            cursor: 'pointer',
            color: '#b9c8d8',
          }}
        >
          Import new cadastre
          <input
            type="file"
            accept=".geojson,.json,.gpkg,.zip,.shp"
            hidden
            onChange={e => {
              const file =
                e.target.files?.[0]

              if (file)
                importLayer(
                  'NEW',
                  file,
                )
            }}
          />
        </label>

        {run && (
          <button
            onClick={openReport}
            style={{
              marginLeft: 'auto',
              padding:
                '9px 13px',
              border:
                '1px solid #36536f',
              borderRadius: 6,
              background:
                '#0d1b2a',
              color: '#dcecff',
              cursor: 'pointer',
            }}
          >
            Generate report
          </button>
        )}
      </div>

      {message && (
        <div
          style={{
            padding: 10,
            borderRadius: 6,
            background:
              '#0e2118',
            border:
              '1px solid #24583b',
            color: '#9be7b4',
            fontSize: 12,
          }}
        >
          {message}
        </div>
      )}

      {error && (
        <div
          style={{
            padding: 10,
            borderRadius: 6,
            background:
              '#291416',
            border:
              '1px solid #71333a',
            color: '#ff9c9c',
            fontSize: 12,
          }}
        >
          {error}
        </div>
      )}

      {run && summary && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns:
              'repeat(4, 1fr)',
            gap: 10,
          }}
        >
          {[
            [
              'Old parcels',
              selectedOldLayer?.parcel_count ??
                summary.old_parcels,
            ],
            [
              'New parcels',
              selectedNewLayer?.parcel_count ??
                summary.new_parcels,
            ],
            [
              'Matched',
              run.comparisons.length,
            ],
            [
              'Changed',
              summary.changed_parcels,
            ],
            [
              'Unchanged',
              summary.unchanged_parcels,
            ],
            [
              'Old area',
              formatArea(
                summary.old_total_area,
              ),
            ],
            [
              'New area',
              formatArea(
                summary.new_total_area,
              ),
            ],
            [
              'Area difference',
              formatArea(
                summary.total_area_difference,
              ),
            ],
            [
              'Boundary shifts',
              run.comparisons.filter(
                x =>
                  x.change_type ===
                  'BOUNDARY_SHIFT',
              ).length,
            ],
          ].map(
            ([label, value]) => (
              <div
                key={String(label)}
                style={{
                  padding: 14,
                  background:
                    '#0c1723',
                  border:
                    '1px solid #223246',
                  borderRadius: 7,
                }}
              >
                <div
                  style={{
                    fontSize: 10,
                    color: '#75879a',
                    marginBottom: 6,
                  }}
                >
                  {label}
                </div>

                <div
                  style={{
                    fontSize: 18,
                    color: '#eaf2fa',
                    fontWeight: 700,
                  }}
                >
                  {String(value)}
                </div>
              </div>
            ),
          )}
        </div>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            'minmax(0, 1fr) 300px',
          gap: 10,
        }}
      >
        <div
          style={{
            minHeight: 500,
            border:
              '1px solid #223246',
            borderRadius: 8,
            background:
              '#07121b',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              padding: 10,
              borderBottom:
                '1px solid #223246',
              display: 'flex',
              gap: 16,
              alignItems: 'center',
              fontSize: 11,
              color: '#9eacbb',
            }}
          >
            <span>
              <b
                style={{
                  color: '#4f9cff',
                }}
              >
                ━
              </b>{' '}
              Old cadastre
            </span>

            <span>
              <b
                style={{
                  color: '#f2b84b',
                }}
              >
                ┅
              </b>{' '}
              New cadastre
            </span>

            <span>
              <b
                style={{
                  color: '#ff6767',
                }}
              >
                ━
              </b>{' '}
              Change
            </span>

            <span
              style={{
                marginLeft: 'auto',
                color: '#71869a',
              }}
            >
              Click a parcel to inspect
            </span>
          </div>

          {geojson ? (
            <svg
              viewBox="0 0 880 500"
              width="100%"
              height="500"
              style={{
                display: 'block',
              }}
            >
              {geojson.features.map(
                (
                  feature,
                  index,
                ) => {
                  const side =
                    feature
                      .properties
                      ?.side

                  const isChange =
                    side ===
                    'CHANGE'

                  const isSelected =
                    selectedComparison
                      ?.id ===
                    feature
                      .properties
                      ?.comparison_id

                  return (
                    <path
                      key={`${side}-${index}`}
                      d={geometryPath(
                        feature.geometry,
                        project,
                      )}
                      fill={
                        isChange
                          ? 'rgba(255,70,70,0.12)'
                          : side === 'OLD'
                          ? 'rgba(55,145,255,0.05)'
                          : 'rgba(245,181,65,0.05)'
                      }
                      stroke={
                        isChange
                          ? '#ff6262'
                          : side === 'OLD'
                          ? '#4f9cff'
                          : '#f2b84b'
                      }
                      strokeWidth={
                        isSelected
                          ? 5
                          : isChange
                          ? 1.5
                          : 2
                      }
                      strokeDasharray={
                        side === 'NEW'
                          ? '7 5'
                          : undefined
                      }
                      opacity={
                        isChange
                          ? isSelected
                            ? 1
                            : 0.55
                          : 1
                      }
                      style={{
                        cursor:
                          feature
                            .properties
                            ?.comparison_id
                            ? 'pointer'
                            : 'default',
                      }}
                      onClick={() => {
                        const comparisonId =
                          feature
                            .properties
                            ?.comparison_id

                        if (!comparisonId)
                          return

                        const match =
                          run?.comparisons.find(
                            x =>
                              x.id ===
                              comparisonId,
                          )

                        if (match)
                          setSelected(
                            match,
                          )
                      }}
                    />
                  )
                },
              )}
            </svg>
          ) : (
            <div
              style={{
                height: 500,
                display: 'grid',
                placeItems:
                  'center',
                color: '#657789',
              }}
            >
              Import/select cadastral
              layers and run comparison.
            </div>
          )}
        </div>

        <div
          style={{
            border:
              '1px solid #223246',
            borderRadius: 8,
            background:
              '#0b1622',
            padding: 14,
          }}
        >
          <div
            style={{
              fontSize: 13,
              fontWeight: 700,
              color: '#e5edf6',
              marginBottom: 12,
            }}
          >
            Parcel comparison
          </div>

          {selectedComparison ? (
            <div>
              <div
                style={{
                  marginBottom: 12,
                  padding: '7px 9px',
                  borderRadius: 5,
                  background: '#10263a',
                  border: '1px solid #31587c',
                  color: '#8fc5ff',
                  fontSize: 10,
                  fontWeight: 700,
                  letterSpacing: 0.8,
                  textTransform: 'uppercase',
                }}
              >
                Selected parcel
              </div>

              <div
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  color: '#eef5fc',
                  marginBottom: 14,
                }}
              >
                {
                  selectedComparison
                    .old_parcel_code
                    || '—'
                }
                {' → '}
                {
                  selectedComparison
                    .new_parcel_code
                    || '—'
                }
              </div>

              {[
                [
                  'Old area',
                  formatArea(
                    selectedComparison.old_area,
                  ),
                ],
                [
                  'New area',
                  formatArea(
                    selectedComparison.new_area,
                  ),
                ],
                [
                  'Area difference',
                  formatArea(
                    selectedComparison.area_difference,
                  ),
                ],
                [
                  'Area change',
                  formatPercent(
                    selectedComparison.area_change_percent,
                  ),
                ],
                [
                  'Old perimeter',
                  formatMeters(
                    selectedComparison.old_perimeter,
                  ),
                ],
                [
                  'New perimeter',
                  formatMeters(
                    selectedComparison.new_perimeter,
                  ),
                ],
                [
                  'Overlap',
                  formatPercent(
                    selectedComparison.overlap_percent,
                  ),
                ],
                [
                  'Centroid shift',
                  formatMeters(
                    selectedComparison.centroid_shift,
                  ),
                ],
                [
                  'Mean boundary difference',
                  formatMeters(
                    selectedComparison.boundary_mean_difference,
                  ),
                ],
                [
                  'Maximum boundary difference',
                  formatMeters(
                    selectedComparison.boundary_max_difference,
                  ),
                ],
              ].map(
                ([label, value]) => (
                  <div
                    key={String(label)}
                    style={{
                      display: 'flex',
                      justifyContent:
                        'space-between',
                      gap: 10,
                      padding:
                        '7px 0',
                      borderBottom:
                        '1px solid #172535',
                      fontSize: 11,
                    }}
                  >
                    <span
                      style={{
                        color: '#7f91a3',
                      }}
                    >
                      {label}
                    </span>

                    <b
                      style={{
                        color: '#dbe8f4',
                      }}
                    >
                      {String(value)}
                    </b>
                  </div>
                ),
              )}

              <div
                style={{
                  marginTop: 14,
                  padding: 10,
                  borderRadius: 6,
                  background:
                    '#241d0d',
                  border:
                    '1px solid #665024',
                  color: '#f0c866',
                  fontWeight: 700,
                  fontSize: 11,
                }}
              >
                {
                  selectedComparison
                    .change_type
                }
              </div>

              <button
                onClick={
                  createVerification
                }
                style={{
                  width: '100%',
                  marginTop: 10,
                  padding: 10,
                  borderRadius: 6,
                  border:
                    '1px solid #31587c',
                  background:
                    '#10263a',
                  color: '#d7ebff',
                  cursor: 'pointer',
                }}
              >
                Create verification case
              </button>
            </div>
          ) : (
            <div
              style={{
                color: '#657789',
                fontSize: 12,
                lineHeight: 1.6,
              }}
            >
              Click a changed parcel
              on the map or select one
              from the comparison table.
            </div>
          )}
        </div>
      </div>

      {run && (
        <div
          style={{
            border:
              '1px solid #223246',
            borderRadius: 8,
            overflow: 'hidden',
            background:
              '#0b1622',
          }}
        >
          <div
            style={{
              padding: 13,
              borderBottom:
                '1px solid #223246',
              fontWeight: 700,
              color: '#e5edf6',
            }}
          >
            Parcel-wise comparison
          </div>

          <div
            style={{
              overflowX: 'auto',
            }}
          >
            <table
              style={{
                width: '100%',
                borderCollapse:
                  'collapse',
                fontSize: 11,
              }}
            >
              <thead>
                <tr>
                  {[
                    'Old ID',
                    'New ID',
                    'Old area',
                    'New area',
                    'Difference',
                    'Overlap',
                    'Boundary',
                    'Change',
                  ].map(
                    heading => (
                      <th
                        key={heading}
                        style={{
                          textAlign:
                            'left',
                          padding: 10,
                          color:
                            '#7f91a3',
                          borderBottom:
                            '1px solid #223246',
                        }}
                      >
                        {heading}
                      </th>
                    ),
                  )}
                </tr>
              </thead>

              <tbody>
                {run.comparisons.map(
                  comparison => (
                    <tr
                      key={
                        comparison.id
                      }
                      onClick={() =>
                        setSelected(
                          comparison,
                        )
                      }
                      title="Click to inspect this parcel"
                      style={{
                        cursor:
                          'pointer',
                        background:
                          selected?.id ===
                          comparison.id
                            ? '#163452'
                            : 'transparent',
                        outline:
                          selected?.id ===
                          comparison.id
                            ? '1px solid #31587c'
                            : 'none',
                        transition:
                          'background 120ms ease',
                      }}
                    >
                      <td
                        style={{
                          padding: 10,
                          fontWeight:
                            selected?.id ===
                            comparison.id
                              ? 700
                              : 400,
                          color:
                            selected?.id ===
                            comparison.id
                              ? '#8fc5ff'
                              : '#dbe6f2',
                        }}
                      >
                        {selected?.id ===
                          comparison.id && (
                          <span
                            style={{
                              marginRight: 6,
                              color: '#4f9cff',
                            }}
                          >
                            ●
                          </span>
                        )}
                        {
                          comparison
                            .old_parcel_code
                        }
                      </td>

                      <td
                        style={{
                          padding: 10,
                        }}
                      >
                        {
                          comparison
                            .new_parcel_code
                        }
                      </td>

                      <td
                        style={{
                          padding: 10,
                        }}
                      >
                        {formatArea(
                          comparison.old_area,
                        )}
                      </td>

                      <td
                        style={{
                          padding: 10,
                        }}
                      >
                        {formatArea(
                          comparison.new_area,
                        )}
                      </td>

                      <td
                        style={{
                          padding: 10,
                        }}
                      >
                        {formatArea(
                          comparison.area_difference,
                        )}
                      </td>

                      <td
                        style={{
                          padding: 10,
                        }}
                      >
                        {formatPercent(
                          comparison.overlap_percent,
                        )}
                      </td>

                      <td
                        style={{
                          padding: 10,
                        }}
                      >
                        {formatMeters(
                          comparison.boundary_max_difference,
                        )}
                      </td>

                      <td
                        style={{
                          padding: 10,
                          fontWeight: 700,
                        }}
                      >
                        {
                          comparison
                            .change_type
                        }
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
