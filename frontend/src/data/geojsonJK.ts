import type { FeatureCollection } from 'geojson';

/**
 * Coordinate bounding box specifically encompassing the 4 representative study districts
 * from Jammu in the south (32.72°N) to Baramulla in the north (34.21°N).
 */
export const JK_STUDY_BOUNDS: [[number, number], [number, number]] = [
  [32.35, 73.95], // South-West corner (South of Jammu City / Samba plain)
  [34.55, 75.45], // North-East corner (North of Baramulla & East of Anantnag)
];

/**
 * GeoJSON polygon representing the Jammu & Kashmir study region
 * Coordinate order: [longitude, latitude] as per GeoJSON specification (RFC 7946).
 */
export const JK_REGION_GEOJSON: FeatureCollection = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'JK-Region',
      properties: {
        name: 'Jammu & Kashmir Region',
        type: 'Regional Study Extent',
        bounding_box: '32.2°N–34.8°N, 73.8°E–75.8°E'
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            // South: Jammu / Kathua / Samba outer plains
            [74.60, 32.40],
            [75.05, 32.35],
            [75.40, 32.45],
            [75.65, 32.70],
            // South-East: Udhampur / Doda / Kishtwar foothills
            [75.55, 33.15],
            [75.45, 33.55],
            // East: Anantnag / Lidder / Greater Himalaya slope
            [75.35, 33.90],
            [75.25, 34.20],
            [74.95, 34.45],
            // North: Bandipora / Baramulla / Kupwara heights
            [74.60, 34.55],
            [74.20, 34.45],
            [73.95, 34.25],
            // West: Line of Control / Uri / Poonch / Rajouri
            [74.05, 33.80],
            [74.20, 33.40],
            [74.35, 33.00],
            [74.50, 32.65],
            [74.60, 32.40]
          ]
        ]
      }
    },
    // Distinct study district polygons
    {
      type: 'Feature',
      id: 'Jammu',
      properties: {
        name: 'Jammu',
        division: 'Jammu Division',
        role: 'Winter Capital & Shivalik Outer Plains',
        elevation: '327m'
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [74.68, 32.60],
            [75.02, 32.58],
            [75.12, 32.82],
            [74.90, 32.90],
            [74.72, 32.80],
            [74.68, 32.60]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      id: 'Srinagar',
      properties: {
        name: 'Srinagar',
        division: 'Kashmir Valley Division',
        role: 'Summer Capital & Central Kashmir Valley',
        elevation: '1585m'
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [74.68, 33.98],
            [74.92, 34.00],
            [74.96, 34.16],
            [74.80, 34.20],
            [74.70, 34.12],
            [74.68, 33.98]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      id: 'Anantnag',
      properties: {
        name: 'Anantnag',
        division: 'Kashmir Valley Division',
        role: 'South Kashmir & Lidder Basin / Pir Panjal',
        elevation: '1600m'
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [75.00, 33.60],
            [75.32, 33.58],
            [75.38, 33.85],
            [75.16, 33.88],
            [75.02, 33.72],
            [75.00, 33.60]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      id: 'Baramulla',
      properties: {
        name: 'Baramulla',
        division: 'Kashmir Valley Division',
        role: 'North Kashmir & Jhelum Valley Gorge',
        elevation: '1593m'
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [74.18, 34.10],
            [74.48, 34.12],
            [74.54, 34.34],
            [74.26, 34.38],
            [74.14, 34.22],
            [74.18, 34.10]
          ]
        ]
      }
    }
  ]
};
