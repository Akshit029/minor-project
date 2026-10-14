/**
 * Central Configuration for J&K Weather Forecast Reliability & Uncertainty System
 * Matches parameters defined in the research project config.yaml and methodology.
 */

export const APP_CONFIG = {
  projectTitle: 'Jammu & Kashmir Forecast Reliability',
  projectSubtitle: 'Spatiotemporal analysis of medium-range weather forecast uncertainty',
  academicBadge: 'B.Tech Minor Project',
  prototypeBadge: 'Research Prototype',
  datasetStatusBadge: 'Operational',
  region: {
    name: 'Jammu & Kashmir',
    bounds: {
      north: 38.0,
      south: 31.0,
      west: 73.0,
      east: 81.0,
    },
    center: [33.4500, 74.8000] as [number, number],
    defaultZoom: 7.5,
  },
  studyDistricts: ['Srinagar', 'Jammu', 'Anantnag', 'Baramulla'] as const,
  forecastHorizon: 'Day 1–10 (24h–240h)',
  modelStatus: 'Operational Baseline',

  // Scientific Alert & Uncertainty Thresholds (Configurable)
  thresholds: {
    // Reliability thresholds (Empirical Reliability Index R in [0, 1])
    reliabilityHigh: 0.70,     // R >= 0.70 -> High reliability
    reliabilityModerate: 0.50, // 0.50 <= R < 0.70 -> Moderate uncertainty
    reliabilityLow: 0.50,      // R < 0.50 -> High uncertainty / Low reliability

    // Forecast-Bust Probability Thresholds
    bustHighProb: 0.70,        // > 70% -> Potential forecast bust (High Risk)
    bustMediumProb: 0.35,      // 35% - 70% -> Elevated bust risk (Medium Risk)
    bustLowProb: 0.35,         // < 35% -> Normal expected variation (Low Risk)

    // Scientific Error Tolerance Scale (engineering standard from config.yaml)
    temperatureErrorScaleC: 2.0, // °C
    precipitationErrorScaleMm: 5.0, // mm
    confidenceFactorK: 10.0,   // Sample confidence parameter k: C = n / (n + k)
    bustQuantile: 0.90,        // 90th percentile of training absolute error
  },

  // Standard scientific naming terms (Mandatory as per Project Rules)
  terminology: {
    forecastSource: 'NOAA GFS Forecast',
    referenceSource: 'ECMWF ERA5 Reference',
    reliabilityIndex: 'Empirical Reliability Index',
    bustProbability: 'Forecast-Bust Probability',
    uncertaintyTerm: 'Forecast Uncertainty',
    disclaimerText: 'Reliability represents an empirical performance index based on historical forecast error and available verification samples. It is not a calibrated probability.',
    referenceNote: 'ECMWF ERA5 is an atmospheric reanalysis reference field and is not treated as absolute ground truth.',
    accumulationGuardNote: 'GFS precipitation represents step-accumulation; ERA5 represents hourly accumulated depth. Direct subtraction without window alignment is strictly guarded against.'
  }
} as const;
