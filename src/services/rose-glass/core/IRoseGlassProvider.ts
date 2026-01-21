/**
 * @fileoverview Rose Glass perception provider interface
 * @module src/services/rose-glass/core/IRoseGlassProvider
 */

import type {
  DimensionalReading,
  LensCalibration,
  PerceptionReport,
  RawPerception,
  RepositoryPerceptionInput,
  CodePerceptionInput,
} from '../types.js';
import type { RequestContext } from '@/utils/index.js';

/**
 * Interface for Rose Glass perception providers
 */
export interface IRoseGlassProvider {
  /**
   * Get available lens calibrations
   */
  getAvailableLenses(): LensCalibration[];

  /**
   * Get specific lens calibration by ID
   */
  getLens(lensId: string): LensCalibration | null;

  /**
   * Calculate overall coherence from dimensional readings
   * @param dimensions - Four-dimensional readings
   * @param weights - Optional weight adjustments
   * @returns Coherence score (0.0-1.0)
   */
  calculateCoherence(
    dimensions: DimensionalReading,
    weights?: {
      psi: number;
      rho: number;
      q: number;
      f: number;
    },
  ): number;

  /**
   * Optimize activation energy using Michaelis-Menten kinetics
   * @param q - Raw activation energy
   * @param Km - Michaelis constant
   * @param Ki - Inhibition constant
   * @returns Optimized activation energy
   */
  optimizeQ(q: number, Km: number, Ki: number): number;

  /**
   * Apply lens calibration to raw perception
   * @param raw - Raw perception data
   * @param lensId - Lens to apply
   * @param context - Request context
   * @returns Calibrated perception report
   */
  applyLens(
    raw: RawPerception,
    lensId: string,
    context: RequestContext,
  ): Promise<PerceptionReport>;

  /**
   * Perceive a repository through Rose Glass
   * @param input - Repository data
   * @param lensId - Optional lens (defaults to code-analysis)
   * @param context - Request context
   * @returns Perception report
   */
  perceiveRepository(
    input: RepositoryPerceptionInput,
    lensId: string | undefined,
    context: RequestContext,
  ): Promise<PerceptionReport>;

  /**
   * Perceive code through Rose Glass
   * @param input - Code data
   * @param lensId - Optional lens
   * @param context - Request context
   * @returns Perception report
   */
  perceiveCode(
    input: CodePerceptionInput,
    lensId: string | undefined,
    context: RequestContext,
  ): Promise<PerceptionReport>;

  /**
   * Health check for the provider
   */
  healthCheck(): Promise<boolean>;
}
