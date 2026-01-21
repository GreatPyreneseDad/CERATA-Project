/**
 * @fileoverview Core Rose Glass perception service
 * @module src/services/rose-glass/rose-glass.service
 */

import { injectable } from 'tsyringe';
import type {
  RawDimensions,
  ExtendedDimensions,
  LensCalibration,
  PerceptionReport,
} from './types.js';
import { optimizeQ } from './biological-optimization.js';
import { codeAnalysisLens } from './calibrations/index.js';

@injectable()
export class RoseGlassService {
  private lenses: Map<string, LensCalibration> = new Map();
  private defaultLens = 'code-analysis';

  constructor() {
    // Register built-in lenses
    this.registerLens(codeAnalysisLens);
  }

  /**
   * Register a lens calibration
   */
  registerLens(calibration: LensCalibration): void {
    this.lenses.set(calibration.name, calibration);
  }

  /**
   * Get lens calibration by name
   */
  getLens(name?: string): LensCalibration {
    const lensName = name ?? this.defaultLens;
    const lens = this.lenses.get(lensName);
    if (!lens) {
      throw new Error(`Unknown lens: ${lensName}`);
    }
    return lens;
  }

  /**
   * Calculate coherence from dimensional readings
   *
   * Formula: C = Ψ + (ρ × Ψ) + q_opt + (f × Ψ) + coupling
   *
   * Where coupling = τ × λ (temporal depth × lens interference)
   * Result scaled to 0-4 range
   */
  calculateCoherence(
    dimensions: ExtendedDimensions,
    lens: LensCalibration,
  ): { coherence: number; qOptimized: number } {
    const { psi, rho, q, f, tau, lambda } = dimensions;
    const { Km, Ki } = lens.biologicalParams;

    // Apply biological optimization to q
    const qOptimized = optimizeQ(q, Km, Ki);

    // Calculate weighted coupling
    const coupling = tau * lambda;

    // Core coherence formula
    const rawCoherence = psi + rho * psi + qOptimized + f * psi + coupling;

    // Scale to 0-4 range (theoretical max ~4.0, practical max ~3.5)
    const coherence = Math.min(4.0, Math.max(0.0, rawCoherence));

    return { coherence, qOptimized };
  }

  /**
   * Main perception method - applies lens to raw dimensions
   */
  perceive(dimensions: RawDimensions, lensName?: string): PerceptionReport {
    const lens = this.getLens(lensName);

    // Extend raw dimensions with temporal and interference estimates
    const extended: ExtendedDimensions = {
      ...dimensions,
      tau: this.estimateTemporalDepth(dimensions),
      lambda: this.estimateLensInterference(dimensions),
    };

    // Calculate coherence with biological optimization
    const { coherence, qOptimized } = this.calculateCoherence(extended, lens);

    // Detect patterns based on lens expectations
    const patterns = this.detectPatterns(extended, lens);

    // Generate warnings for concerning patterns
    const warnings = this.generateWarnings(extended, coherence);

    // Assess confidence in the reading
    const confidence = this.assessConfidence(extended);

    return {
      lens: lens.name,
      dimensions: extended,
      coherence,
      qOptimized,
      confidence,
      patterns,
      warnings,
    };
  }

  /**
   * Estimate temporal depth (τ) from dimensional signals
   *
   * High ρ (accumulated wisdom) suggests temporal depth
   * High Ψ (consistency) suggests established patterns over time
   */
  private estimateTemporalDepth(d: RawDimensions): number {
    // Temporal depth correlates with accumulated wisdom and consistency
    const rawTau = d.rho * 0.6 + d.psi * 0.4;
    return Math.min(1.0, Math.max(0.0, rawTau));
  }

  /**
   * Estimate lens interference (λ) from dimensional signals
   *
   * High λ indicates dimensional conflict or observer effects
   * Low consistency + high activation = high interference
   */
  private estimateLensInterference(d: RawDimensions): number {
    // Interference occurs when activation is high but consistency is low
    const inconsistency = 1.0 - d.psi;
    const rawLambda = inconsistency * d.q * 0.5;
    return Math.min(1.0, Math.max(0.0, rawLambda));
  }

  /**
   * Detect patterns based on lens expectations and thresholds
   */
  private detectPatterns(
    d: ExtendedDimensions,
    lens: LensCalibration,
  ): string[] {
    const detected: string[] = [];

    // Pattern detection thresholds
    if (d.psi >= 0.7) detected.push('high-consistency');
    if (d.psi <= 0.3) detected.push('low-consistency');

    if (d.rho >= 0.7) detected.push('battle-tested');
    if (d.rho <= 0.3) detected.push('immature');

    if (d.q >= 0.7) detected.push('high-activation');
    if (d.q <= 0.2) detected.push('dormant');

    if (d.f >= 0.7) detected.push('well-integrated');
    if (d.f <= 0.3) detected.push('isolated');

    if (d.tau >= 0.7) detected.push('deep-history');
    if (d.tau <= 0.3) detected.push('ephemeral');

    if (d.lambda >= 0.5) detected.push('observer-interference');

    // Cross-dimensional patterns
    if (d.psi >= 0.7 && d.rho >= 0.7) detected.push('stable-mature');
    if (d.psi <= 0.3 && d.q >= 0.7) detected.push('chaotic-active');
    if (d.f >= 0.7 && d.rho >= 0.7) detected.push('ecosystem-anchor');

    return detected;
  }

  /**
   * Generate warnings for concerning dimensional patterns
   */
  private generateWarnings(d: ExtendedDimensions, coherence: number): string[] {
    const warnings: string[] = [];

    // Low coherence warning
    if (coherence < 1.0) {
      warnings.push('Low overall coherence - substrate may be unstable');
    }

    // Dimensional conflict warnings
    if (d.psi <= 0.3 && d.q >= 0.7) {
      warnings.push(
        'High activation with low consistency - potential instability',
      );
    }

    if (d.f <= 0.3 && d.rho >= 0.5) {
      warnings.push('Isolated despite maturity - integration issues');
    }

    if (d.lambda >= 0.6) {
      warnings.push('High observer interference - perception may be distorted');
    }

    // Biological optimization warnings
    if (d.q >= 0.9) {
      warnings.push(
        'Extreme activation detected - biological optimization applied',
      );
    }

    // Temporal warnings
    if (d.tau <= 0.2 && d.rho >= 0.5) {
      warnings.push(
        'Shallow temporal depth despite accumulated wisdom - anomaly',
      );
    }

    return warnings;
  }

  /**
   * Assess confidence in perception reading
   *
   * High confidence: Strong signals, low interference
   * Medium confidence: Mixed signals or moderate interference
   * Low confidence: Weak signals or high interference
   */
  private assessConfidence(d: ExtendedDimensions): 'low' | 'medium' | 'high' {
    // Calculate signal strength (average of core dimensions)
    const signalStrength = (d.psi + d.rho + d.q + d.f) / 4;

    // High interference reduces confidence
    const interferenceAdjusted = signalStrength * (1.0 - d.lambda * 0.5);

    if (interferenceAdjusted >= 0.6) return 'high';
    if (interferenceAdjusted >= 0.35) return 'medium';
    return 'low';
  }
}
