/**
 * @fileoverview LinguisticLens nematocyst - Ψ/q/ρ natural language perception
 * @module mcp-server/tools/definitions/cerata-linguistic-lens
 */

import { z } from 'zod';
import type { ToolDefinition, SdkContext } from '../utils/toolDefinition.js';
import { executePythonScript } from '@/utils/python-executor.js';
import type { RequestContext } from '@/utils/internal/requestContext.js';
import { McpError, JsonRpcErrorCode } from '@/types-global/errors.js';
import { markdown } from '@/utils/index.js';
import type { ContentBlock } from '@/types-global/mcp.js';

// ==================== Constants ====================

const TOOL_NAME = 'cerata_linguistic_lens';
const TOOL_TITLE = 'LinguisticLens - Ψ/q/ρ Perception';
const TOOL_DESCRIPTION = `
Perceives linguistic coherence (Ψ), activation (q), and wisdom (ρ) through spaCy NLP analysis.

**Origin:** Metabolized from spacy/spacy repository
**Generation:** 3
**Capability:** Extracts Ψ/q/ρ dimensions from natural language text

**Input:** Text to analyze + optional spaCy model
**Output:** Multi-dimensional reading with coherence assessment
**Models:** en_core_web_sm (default), en_core_web_md, en_core_web_lg
`.trim();

const TOOL_ANNOTATIONS = {
  readOnlyHint: true,
  idempotentHint: true,
};

// ==================== Schemas ====================

const InputSchema = z.object({
  text: z.string().min(1).describe('Text to analyze for linguistic perception'),
  model: z
    .enum(['en_core_web_sm', 'en_core_web_md', 'en_core_web_lg'])
    .default('en_core_web_sm')
    .describe('spaCy model to use for analysis'),
});

const CoherenceSchema = z.object({
  Ψ: z.number().describe('Psi - Internal consistency (0-1)'),
  q: z.number().describe('q - Moral/emotional activation (0-1)'),
  ρ: z.number().describe('Rho - Accumulated wisdom (0-1)'),
  overall: z.number().describe('Overall coherence score'),
  pattern: z.string().describe('Detected coherence pattern'),
});

const OutputSchema = z.object({
  success: z.boolean().describe('Whether the perception succeeded'),
  reading: z
    .object({
      psi: z.number().describe('Ψ - Internal consistency (0-1)'),
      rho: z.number().describe('ρ - Accumulated wisdom (0-1)'),
      q: z.number().describe('q - Activation energy (0-1)'),
      coherence: CoherenceSchema.describe(
        'Multi-dimensional coherence assessment',
      ),
      pos_pattern: z.string().describe('Part-of-speech pattern detected'),
      entity_count: z.number().describe('Named entity count'),
      confidence: z.number().describe('Reading confidence (0-1)'),
      notes: z.array(z.string()).describe('Perception insights'),
    })
    .optional()
    .describe('Linguistic reading'),
  error: z.string().optional().describe('Error message if failed'),
  model: z.string().describe('spaCy model used'),
});

type Input = z.infer<typeof InputSchema>;
type Output = z.infer<typeof OutputSchema>;

// ==================== Logic ====================

/**
 * Execute LinguisticLens perception via Python nematocyst
 */
async function linguisticLensLogic(
  input: Input,
  appContext: RequestContext,
  _sdkContext: SdkContext,
): Promise<Output> {
  const { text, model } = input;

  // Execute Python CLI wrapper
  const result = await executePythonScript<Output>(
    {
      scriptPath: 'integrations/spacy/cli.py',
      input: {
        text,
        model,
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
      `LinguisticLens perception failed: ${result.error || 'Unknown error'}`,
      {
        errorType: result.errorType,
        stderr: result.stderr,
      },
    );
  }

  return result as Output;
}

// ==================== Formatter ====================

function formatLinguisticLensResponse(output: Output): ContentBlock[] {
  const md = markdown();

  md.h1('📝 LinguisticLens Perception — Ψ/q/ρ Dimensions');

  if (!output.success) {
    md.h2('❌ Perception Failed');
    md.text(output.error || 'Unknown error');
    return [{ type: 'text', text: md.build() }];
  }

  const reading = output.reading!;

  md.h2('🎯 Multi-Dimensional Analysis');
  md.keyValue('Model', output.model);
  md.keyValue('Confidence', reading.confidence.toFixed(3));
  md.blank();

  md.h2('📐 Core Dimensions');
  md.list([
    `**Ψ (Internal Consistency):** ${reading.psi.toFixed(3)} — Structural coherence`,
    `**ρ (Accumulated Wisdom):** ${reading.rho.toFixed(3)} — Linguistic sophistication`,
    `**q (Activation Energy):** ${reading.q.toFixed(3)} — Emotional/moral activation`,
  ]);
  md.blank();

  md.h2('🔍 Coherence Assessment');
  md.keyValue('Overall Coherence', reading.coherence.overall.toFixed(3));
  md.keyValue('Pattern', reading.coherence.pattern);
  md.blank();

  md.h3('Dimension Breakdown');
  md.list([
    `**Ψ (Consistency):** ${reading.coherence.Ψ.toFixed(3)}`,
    `**ρ (Wisdom):** ${reading.coherence.ρ.toFixed(3)}`,
    `**q (Activation):** ${reading.coherence.q.toFixed(3)}`,
  ]);
  md.blank();

  md.h2('📊 Linguistic Metrics');
  md.keyValue('POS Pattern', reading.pos_pattern);
  md.keyValue('Entity Count', reading.entity_count.toString());
  md.blank();

  if (reading.notes.length > 0) {
    md.h2('💡 Insights');
    md.list(reading.notes);
  }

  return [{ type: 'text', text: md.build() }];
}

// ==================== Export ====================

export const linguisticLensToolDefinition: ToolDefinition<Input, Output> = {
  name: TOOL_NAME,
  title: TOOL_TITLE,
  description: TOOL_DESCRIPTION,
  inputSchema: InputSchema,
  outputSchema: OutputSchema,
  logic: linguisticLensLogic,
  annotations: TOOL_ANNOTATIONS,
  responseFormatter: formatLinguisticLensResponse,
};
