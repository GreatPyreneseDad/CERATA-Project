/**
 * @fileoverview Biological optimization using Michaelis-Menten enzyme kinetics
 * @module src/services/rose-glass/biological-optimization
 */

/**
 * Michaelis-Menten enzyme kinetics applied to emotional activation.
 * Prevents synthetic amplification of extreme states.
 *
 * q_opt = q / (Km + q + q²/Ki)
 *
 * @param q - Raw activation energy (0-1)
 * @param Km - Saturation constant (default: 0.2)
 * @param Ki - Inhibition constant (default: 0.8)
 * @returns Optimized activation energy
 */
export function optimizeQ(
  q: number,
  Km: number = 0.2,
  Ki: number = 0.8,
): number {
  if (q <= 0) return 0;
  if (q >= 1) q = 0.999; // Prevent division issues

  const denominator = Km + q + (q * q) / Ki;
  return q / denominator;
}

/**
 * Returns optimization curve characteristics for debugging.
 *
 * @param Km - Saturation constant
 * @param Ki - Inhibition constant
 * @param steps - Number of curve points
 * @returns Array of {q, qOpt} pairs
 */
export function getOptimizationCurve(
  Km: number = 0.2,
  Ki: number = 0.8,
  steps: number = 10,
): Array<{ q: number; qOpt: number }> {
  return Array.from({ length: steps + 1 }, (_, i) => {
    const q = i / steps;
    return { q, qOpt: optimizeQ(q, Km, Ki) };
  });
}
