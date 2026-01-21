/**
 * @fileoverview WisdomLens nematocyst - ρ-dimension mathematical rigor perception
 * @module mcp-server/tools/definitions/cerata-wisdom-lens
 */

import { z } from 'zod';
import type { ToolDefinition, SdkContext } from '../utils/toolDefinition.js';
import { executePythonScript } from '@/utils/python-executor.js';
import type { RequestContext } from '@/utils/internal/requestContext.js';
import { McpError, JsonRpcErrorCode } from '@/types-global/errors.js';
import { markdown } from '@/utils/index.js';
import type { ContentBlock } from '@/types-global/mcp.js';

// ==================== Constants ====================

const TOOL_NAME = 'cerata_wisdom_lens';
const TOOL_TITLE = 'WisdomLens - ρ-Dimension Perception';
const TOOL_DESCRIPTION = `
Perceives mathematical rigor (ρ-dimension) through NumPy analysis.

**Origin:** Metabolized from numpy/numpy repository
**Generation:** 2
**Capability:** Assesses consistency, precision, stability, and convergence in numerical data

**Input:** Array of numbers
**Output:** ρ-dimension reading with rigor metrics
**Cultural Calibrations:** practical, academic, indigenous_oral, contemplative
`.trim();

const TOOL_ANNOTATIONS = {
  readOnlyHint: true,
  idempotentHint: true,
};

// ==================== Schemas ====================

const InputSchema = z.object({
  data: z
    .array(z.number())
    .min(1)
    .describe('Array of numerical values to analyze for mathematical rigor'),
  calibration: z
    .enum(['practical', 'academic', 'indigenous_oral', 'contemplative'])
    .default('practical')
    .describe('Cultural calibration for wisdom assessment weights'),
  context: z
    .enum([
      'general',
      'financial',
      'scientific',
      'statistical',
      'communication',
    ])
    .default('general')
    .describe('Mathematical context for precision assessment'),
});

const OutputSchema = z.object({
  success: z.boolean().describe('Whether the perception succeeded'),
  reading: z
    .object({
      rho: z.number().describe('Overall ρ-dimension score (0-1)'),
      consistency: z
        .number()
        .describe('Coefficient of variation analysis (0-1)'),
      precision: z
        .number()
        .describe('Context-appropriate decimal precision (0-1)'),
      stability: z.number().describe('Perturbation resistance (0-1)'),
      convergence: z.number().describe('Variance trend over time (0-1)'),
      confidence: z.number().describe('Reading confidence (0-1)'),
      context: z.string().describe('Mathematical context used'),
      notes: z.array(z.string()).describe('Perception insights'),
    })
    .optional()
    .describe('ρ-dimension reading'),
  error: z.string().optional().describe('Error message if failed'),
  calibration: z.string().describe('Cultural calibration used'),
});

type Input = z.infer<typeof InputSchema>;
type Output = z.infer<typeof OutputSchema>;

// ==================== Logic ====================

/**
 * Execute WisdomLens perception via Python nematocyst
 */
async function wisdomLensLogic(
  input: Input,
  appContext: RequestContext,
  _sdkContext: SdkContext,
): Promise<Output> {
  const { data, calibration, context } = input;

  // Execute Python CLI wrapper
  const result = await executePythonScript<Output>(
    {
      scriptPath: 'integrations/numpy/cli.py',
      input: {
        data,
        calibration,
        context,
      },
      timeout: 30000,
      cwd: process.cwd(),
    },
    appContext,
  );

  // Check for Python-level errors
  if (!result.success) {
    throw new McpError(
      JsonRpcErrorCode.InternalError,
      `WisdomLens perception failed: ${result.error || 'Unknown error'}`,
      {
        errorType: result.errorType,
        stderr: result.stderr,
      },
    );
  }

  return result as Output;
}

// ==================== Formatter ====================

function formatWisdomLensResponse(output: Output): ContentBlock[] {
  const md = markdown();

  md.h1('🔬 WisdomLens Perception — ρ-Dimension');

  if (!output.success) {
    md.h2('❌ Perception Failed');
    md.text(output.error || 'Unknown error');
    return [{ type: 'text', text: md.build() }];
  }

  const reading = output.reading!;

  md.h2('📊 Mathematical Rigor Assessment');
  md.keyValue('ρ (Overall Rigor)', reading.rho.toFixed(3));
  md.keyValue('Calibration', output.calibration);
  md.keyValue('Context', reading.context);
  md.keyValue('Confidence', reading.confidence.toFixed(3));
  md.blank();

  md.h2('🔍 Rigor Dimensions');
  md.list([
    `**Consistency:** ${reading.consistency.toFixed(3)} — Coefficient of variation analysis`,
    `**Precision:** ${reading.precision.toFixed(3)} — Context-appropriate decimal places`,
    `**Stability:** ${reading.stability.toFixed(3)} — Perturbation resistance`,
    `**Convergence:** ${reading.convergence.toFixed(3)} — Variance trend over time`,
  ]);
  md.blank();

  if (reading.notes.length > 0) {
    md.h2('💡 Insights');
    md.list(reading.notes);
  }

  return [{ type: 'text', text: md.build() }];
}

// ==================== Export ====================

export const wisdomLensToolDefinition: ToolDefinition<Input, Output> = {
  name: TOOL_NAME,
  title: TOOL_TITLE,
  description: TOOL_DESCRIPTION,
  inputSchema: InputSchema,
  outputSchema: OutputSchema,
  logic: wisdomLensLogic,
  annotations: TOOL_ANNOTATIONS,
  responseFormatter: formatWisdomLensResponse,
};
