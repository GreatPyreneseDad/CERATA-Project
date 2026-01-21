/**
 * @fileoverview Rose Glass perception types
 * @module src/services/rose-glass/types
 */

export interface RawDimensions {
  psi: number; // Ψ - Internal consistency (0-1)
  rho: number; // ρ - Accumulated wisdom (0-1)
  q: number; // q - Moral/emotional activation (0-1)
  f: number; // f - Social belonging (0-1)
}

export interface ExtendedDimensions extends RawDimensions {
  tau: number; // τ - Temporal depth (0-1)
  lambda: number; // λ - Lens interference (0-1)
}

export interface BiologicalParams {
  Km: number; // Saturation constant (default: 0.2)
  Ki: number; // Inhibition constant (default: 0.8)
}

export interface LensCalibration {
  name: string;
  description: string;
  weights: {
    psi: number;
    rho: number;
    q: number;
    f: number;
  };
  biologicalParams: BiologicalParams;
  expectedPatterns?: string[]; // What this lens looks for
}

export interface PerceptionReport {
  lens: string;
  dimensions: ExtendedDimensions;
  coherence: number; // 0-4 scale
  qOptimized: number; // Post biological optimization
  confidence: 'low' | 'medium' | 'high';
  patterns: string[]; // Detected patterns
  warnings: string[]; // Perception concerns
}
