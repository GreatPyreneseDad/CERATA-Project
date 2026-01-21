/**
 * @fileoverview Code analysis lens calibration
 * @module src/services/rose-glass/calibrations/code-analysis
 */

import type { LensCalibration } from '../types.js';

export const codeAnalysisLens: LensCalibration = {
  name: 'code-analysis',
  description: 'Perceives code repository coherence patterns',

  weights: {
    psi: 0.3, // Internal consistency highly valued
    rho: 0.3, // Accumulated wisdom (battle-tested)
    q: 0.15, // Activity level matters less
    f: 0.25, // Ecosystem fit important
  },

  biologicalParams: {
    Km: 0.2,
    Ki: 0.8,
  },

  expectedPatterns: [
    'error-handling',
    'type-safety',
    'test-coverage',
    'documentation',
    'consistent-style',
    'modular-structure',
    'dependency-hygiene',
  ],
};
