/**
 * @fileoverview BelongingLens nematocyst - f-dimension relational graph perception
 * @module mcp-server/tools/definitions/cerata-belonging-lens
 */

import { z } from 'zod';
import type { ToolDefinition, SdkContext } from '../utils/toolDefinition.js';
import { executePythonScript } from '@/utils/python-executor.js';
import type { RequestContext } from '@/utils/internal/requestContext.js';
import { McpError, JsonRpcErrorCode } from '@/types-global/errors.js';
import { markdown, type MarkdownBuilder } from '@/utils/index.js';
import type { ContentBlock } from '@/types-global/mcp.js';

// ==================== Constants ====================

const TOOL_NAME = 'cerata_belonging_lens';
const TOOL_TITLE = 'BelongingLens - f-Dimension Perception';
const TOOL_DESCRIPTION = `
Perceives social belonging (f-dimension) through NetworkX graph centrality analysis.

**Origin:** Metabolized from networkx/networkx repository
**Generation:** 2
**Capability:** Assesses local/bridge/influence/reach positions in relational graphs

**Input:** Graph structure (nodes, edges) + optional target node
**Output:** f-dimension reading(s) with centrality metrics
**Cultural Calibrations:** modern_social, traditional_community, organizational, research_network
`.trim();

const TOOL_ANNOTATIONS = {
  readOnlyHint: true,
  idempotentHint: true,
};

// ==================== Schemas ====================

const InputSchema = z.object({
  nodes: z
    .array(z.string())
    .min(1)
    .describe('Array of node identifiers in the graph'),
  edges: z
    .array(z.tuple([z.string(), z.string()]))
    .describe('Array of edge pairs [[source, target], ...]'),
  node: z
    .string()
    .optional()
    .describe(
      'Optional: specific node to analyze (if omitted, analyzes all nodes)',
    ),
  calibration: z
    .enum([
      'modern_social',
      'traditional_community',
      'organizational',
      'research_network',
    ])
    .default('modern_social')
    .describe('Cultural calibration for belonging assessment weights'),
  directed: z
    .boolean()
    .default(false)
    .describe('Whether the graph is directed'),
});

const ReadingSchema = z.object({
  f: z.number().describe('Overall f-dimension score (0-1)'),
  local_f: z.number().describe('Degree centrality - local connectivity (0-1)'),
  bridge_f: z
    .number()
    .describe('Betweenness centrality - bridging position (0-1)'),
  influence_f: z
    .number()
    .describe('Eigenvector centrality - influential connections (0-1)'),
  reach_f: z.number().describe('Closeness centrality - network reach (0-1)'),
  confidence: z.number().describe('Reading confidence (0-1)'),
  node_id: z.string().describe('Node identifier'),
  notes: z.array(z.string()).describe('Perception insights'),
});

const OutputSchema = z.object({
  success: z.boolean().describe('Whether the perception succeeded'),
  reading: ReadingSchema.optional().describe('Single node f-dimension reading'),
  readings: z
    .record(z.string(), ReadingSchema)
    .optional()
    .describe('All nodes f-dimension readings'),
  node_count: z.number().optional().describe('Total nodes analyzed'),
  error: z.string().optional().describe('Error message if failed'),
  calibration: z.string().describe('Cultural calibration used'),
});

type Input = z.infer<typeof InputSchema>;
type Output = z.infer<typeof OutputSchema>;
type Reading = z.infer<typeof ReadingSchema>;

// ==================== Logic ====================

/**
 * Execute BelongingLens perception via Python nematocyst
 */
async function belongingLensLogic(
  input: Input,
  appContext: RequestContext,
  _sdkContext: SdkContext,
): Promise<Output> {
  const { nodes, edges, node, calibration, directed } = input;

  // Execute Python CLI wrapper
  const result = await executePythonScript<Output>(
    {
      scriptPath: 'integrations/networkx/cli.py',
      input: {
        nodes,
        edges,
        node,
        calibration,
        directed,
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
      `BelongingLens perception failed: ${result.error || 'Unknown error'}`,
      {
        errorType: result.errorType,
        stderr: result.stderr,
      },
    );
  }

  return result as Output;
}

// ==================== Formatter ====================

function formatReadingDetails(reading: Reading, md: MarkdownBuilder) {
  md.keyValue('f (Overall Belonging)', reading.f.toFixed(3));
  md.blank();

  md.h3('🔍 Centrality Dimensions');
  md.list([
    `**Local:** ${reading.local_f.toFixed(3)} — Degree centrality (connectivity)`,
    `**Bridge:** ${reading.bridge_f.toFixed(3)} — Betweenness centrality (bridging)`,
    `**Influence:** ${reading.influence_f.toFixed(3)} — Eigenvector centrality (connections)`,
    `**Reach:** ${reading.reach_f.toFixed(3)} — Closeness centrality (network reach)`,
  ]);
  md.blank();

  if (reading.notes.length > 0) {
    md.h3('💡 Insights');
    md.list(reading.notes);
  }
}

function formatBelongingLensResponse(output: Output): ContentBlock[] {
  const md = markdown();

  md.h1('🕸️ BelongingLens Perception — f-Dimension');

  if (!output.success) {
    md.h2('❌ Perception Failed');
    md.text(output.error || 'Unknown error');
    return [{ type: 'text', text: md.build() }];
  }

  md.keyValue('Calibration', output.calibration);
  md.blank();

  if (output.reading) {
    // Single node analysis
    const reading = output.reading;
    md.h2(`📍 Node: ${reading.node_id}`);
    md.keyValue('Confidence', reading.confidence.toFixed(3));
    md.blank();

    formatReadingDetails(reading, md);
  } else if (output.readings) {
    // Network-wide analysis
    md.h2('🌐 Network Analysis');
    md.keyValue('Total Nodes', output.node_count?.toString() || '0');
    md.blank();

    // Sort by f-dimension score
    const sortedNodes = Object.entries(output.readings).sort(
      ([, a], [, b]) => b.f - a.f,
    );

    md.h2('📊 Top 10 Nodes by Belonging');
    const topNodes = sortedNodes.slice(0, 10);
    md.list(
      topNodes.map(
        ([nodeId, reading]) =>
          `**${nodeId}:** f=${reading.f.toFixed(3)} (local=${reading.local_f.toFixed(2)}, bridge=${reading.bridge_f.toFixed(2)})`,
      ),
    );
    md.blank();

    // Show detailed analysis for top node
    if (topNodes.length > 0) {
      const [topNodeId, topReading] = topNodes[0]!;
      md.h2(`🏆 Most Central Node: ${topNodeId}`);
      formatReadingDetails(topReading, md);
    }
  }

  return [{ type: 'text', text: md.build() }];
}

// ==================== Export ====================

export const belongingLensToolDefinition: ToolDefinition<Input, Output> = {
  name: TOOL_NAME,
  title: TOOL_TITLE,
  description: TOOL_DESCRIPTION,
  inputSchema: InputSchema,
  outputSchema: OutputSchema,
  logic: belongingLensLogic,
  annotations: TOOL_ANNOTATIONS,
  responseFormatter: formatBelongingLensResponse,
};
