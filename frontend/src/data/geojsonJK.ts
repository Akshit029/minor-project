import type { FeatureCollection } from 'geojson';

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
        bounding_box: '31.0°N–38.0°N, 73.0°E–81.0°E'
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [73.8, 32.5],
            [74.2, 32.2],
            [74.9, 32.4],
            [75.8, 32.3],
            [76.5, 32.7],
            [77.2, 33.2],
            [77.9, 33.8],
            [78.4, 34.5],
            [77.8, 35.2],
            [76.8, 35.8],
            [75.5, 36.1],
            [74.5, 35.6],
            [73.9, 34.8],
            [73.6, 34.2],
            [73.7, 33.3],
            [73.8, 32.5]
          ]
        ]
      }
    },
    // Approximate territorial polygons for the 4 study districts to give rich spatial map overlay
    {
      type: 'Feature',
      id: 'Srinagar',
      properties: {
        name: 'Srinagar',
        role: 'Summer Capital & Kashmir Central Valley',
        elevation: '1585m'
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [74.70, 34.00],
            [74.90, 34.02],
            [74.94, 34.14],
            [74.82, 34.18],
            [74.72, 34.11],
            [74.70, 34.00]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      id: 'Jammu',
      properties: {
        name: 'Jammu',
        role: 'Winter Capital & Shivalik Plains',
        elevation: '327m'
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [74.72, 32.65],
            [74.96, 32.62],
            [75.05, 32.78],
            [74.88, 32.85],
            [74.75, 32.76],
            [74.72, 32.65]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      id: 'Anantnag',
      properties: {
        name: 'Anantnag',
        role: 'South Kashmir & Lidder Basin',
        elevation: '1600m'
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [75.04, 33.65],
            [75.28, 33.62],
            [75.35, 33.82],
            [75.18, 33.86],
            [75.06, 33.74],
            [75.04, 33.65]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      id: 'Baramulla',
      properties: {
        name: 'Baramulla',
        role: 'North Kashmir & Jhelum Gorge',
        elevation: '1593m'
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [74.22, 34.12],
            [74.45, 34.14],
            [74.50, 34.32],
            [74.28, 34.35],
            [74.18, 34.22],
            [74.22, 34.12]
          ]
        ]
      }
    }
  ]
};
