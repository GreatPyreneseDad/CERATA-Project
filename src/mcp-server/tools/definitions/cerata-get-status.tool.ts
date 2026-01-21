/**
 * @fileoverview CERATA instance status tool - reports current body state
 * @module src/mcp-server/tools/definitions/cerata-get-status.tool
 */
import type { ContentBlock } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

import type {
  SdkContext,
  ToolAnnotations,
  ToolDefinition,
} from '@/mcp-server/tools/utils/index.js';
import { markdown } from '@/utils/index.js';
import { withToolAuth } from '@/mcp-server/transports/auth/lib/withAuth.js';
import { type RequestContext, logger } from '@/utils/index.js';
import { container } from 'tsyringe';
import { StorageService } from '@/container/tokens.js';
import type { StorageService as StorageServiceType } from '@/storage/core/StorageService.js';

/** Tool name following CERATA naming convention */
const TOOL_NAME = 'cerata_get_status';

/** Human-readable title */
const TOOL_TITLE = 'CERATA Get Status';

/** LLM-facing description */
const TOOL_DESCRIPTION =
  'Returns the current state of this CERATA instance: instance ID, capabilities manifest, active trials, hunt history, and storage health. Read-only diagnostic tool.';

/** Tool annotations - read-only, idempotent, no external world interaction */
const TOOL_ANNOTATIONS: ToolAnnotations = {
  readOnlyHint: true,
  idempotentHint: true,
  openWorldHint: false,
};

//
// Storage keys for CERATA state
//
const STORAGE_KEYS = {
  instanceId: 'cerata:instance:id',
  instanceCreated: 'cerata:instance:created',
  capabilitiesManifest: 'cerata:capabilities:manifest',
  huntHistoryPrefix: 'cerata:hunt:',
  trialsPrefix: 'cerata:trials:',
} as const;

//
// Schemas
//
const InputSchema = z
  .object({
    instanceId: z
      .string()
      .optional()
      .describe(
        'Optional: Query status of a specific instance ID. Omit for current instance.',
      ),
  })
  .describe('Get CERATA instance status');

const OutputSchema = z
  .object({
    instanceId: z
      .string()
      .describe('Unique identifier for this CERATA instance'),
    createdAt: z
      .string()
      .datetime()
      .describe('ISO 8601 timestamp when instance was initialized'),
    capabilities: z
      .object({
        count: z
          .number()
          .int()
          .min(0)
          .describe('Number of deployed nematocysts'),
        domains: z.array(z.string()).describe('Capability domains available'),
      })
      .describe('Deployed capabilities manifest'),
    trials: z
      .object({
        active: z
          .number()
          .int()
          .min(0)
          .describe('Number of active trials (classic vs experimental)'),
      })
      .describe('Current trial state'),
    huntHistory: z
      .object({
        totalHunts: z
          .number()
          .int()
          .min(0)
          .describe('Total repositories hunted'),
      })
      .describe('Hunting activity'),
    storage: z
      .object({
        healthy: z.boolean().describe('Storage provider connectivity status'),
        provider: z.string().describe('Storage provider type'),
      })
      .describe('Storage health'),
  })
  .describe('CERATA instance status report');

type GetStatusInput = z.infer<typeof InputSchema>;
type GetStatusOutput = z.infer<typeof OutputSchema>;

//
// Pure business logic
//
async function getStatusLogic(
  input: GetStatusInput,
  appContext: RequestContext,
  _sdkContext: SdkContext,
): Promise<GetStatusOutput> {
  logger.debug('Retrieving CERATA instance status', {
    ...appContext,
    requestedInstanceId: input.instanceId,
  });

  const storage = container.resolve<StorageServiceType>(StorageService);

  // Use default tenant for CERATA instance-level state
  // (This is the body's own state, not user-specific)
  const tenantId = 'cerata-system';
  const context: RequestContext = {
    ...appContext,
    tenantId,
  };

  // Get or initialize instance ID
  let instanceId = await storage.get<string>(STORAGE_KEYS.instanceId, context);
  let createdAt: string;

  if (!instanceId) {
    // First boot - initialize instance
    instanceId = crypto.randomUUID();
    createdAt = new Date().toISOString();

    await storage.set(STORAGE_KEYS.instanceId, instanceId, context);
    await storage.set(STORAGE_KEYS.instanceCreated, createdAt, context);

    // Initialize empty capabilities manifest
    await storage.set(
      STORAGE_KEYS.capabilitiesManifest,
      {
        domains: [],
        nematocysts: {},
      },
      context,
    );

    logger.info('CERATA instance initialized', {
      ...context,
      instanceId,
      createdAt,
    });
  } else {
    const storedCreatedAt = await storage.get<string>(
      STORAGE_KEYS.instanceCreated,
      context,
    );
    createdAt = storedCreatedAt ?? new Date().toISOString();
  }

  // Get capabilities manifest
  const capabilitiesData = await storage.get<{
    domains: string[];
    nematocysts: Record<string, unknown>;
  }>(STORAGE_KEYS.capabilitiesManifest, context);

  const capabilities = {
    count: capabilitiesData?.domains?.length ?? 0,
    domains: capabilitiesData?.domains ?? [],
  };

  // Count active trials
  const trialKeys = await storage.list(STORAGE_KEYS.trialsPrefix, context);
  const trials = {
    active: trialKeys.keys.length,
  };

  // Count hunt history
  const huntKeys = await storage.list(STORAGE_KEYS.huntHistoryPrefix, context);
  const huntHistory = {
    totalHunts: huntKeys.keys.length,
  };

  // Storage health check (simple connectivity test)
  let storageHealthy = true;
  let providerType: string = 'unknown';
  try {
    // Attempt a simple read operation
    await storage.get('healthcheck', context);
    // Get provider type from config
    const { AppConfig } = await import('@/container/tokens.js');

    const config = container.resolve(AppConfig);
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    providerType = config.storage.providerType as string;
  } catch (error) {
    storageHealthy = false;
    logger.error('Storage health check failed', {
      ...context,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }

  return {
    instanceId,
    createdAt,
    capabilities,
    trials,
    huntHistory,
    storage: {
      healthy: storageHealthy,
      provider: providerType,
    },
  };
}

/**
 * Response formatter - creates a concise markdown status report
 */
function responseFormatter(result: GetStatusOutput): ContentBlock[] {
  const md = markdown()
    .heading(2, 'CERATA Instance Status')
    .heading(3, 'Identity')
    .bulletList([
      `**Instance ID:** \`${result.instanceId}\``,
      `**Created:** ${new Date(result.createdAt).toLocaleString()}`,
    ])
    .heading(3, 'Capabilities')
    .bulletList([
      `**Deployed Nematocysts:** ${result.capabilities.count}`,
      `**Domains:** ${result.capabilities.domains.length > 0 ? result.capabilities.domains.join(', ') : 'None'}`,
    ])
    .heading(3, 'Activity')
    .bulletList([
      `**Active Trials:** ${result.trials.active}`,
      `**Total Hunts:** ${result.huntHistory.totalHunts}`,
    ])
    .heading(3, 'Storage')
    .bulletList([
      `**Provider:** ${result.storage.provider}`,
      `**Status:** ${result.storage.healthy ? '✅ Healthy' : '❌ Unhealthy'}`,
    ]);

  return [
    {
      type: 'text',
      text: md.build(),
    },
  ];
}

/**
 * The complete tool definition for CERATA instance status
 */
export const cerataGetStatusTool: ToolDefinition<
  typeof InputSchema,
  typeof OutputSchema
> = {
  name: TOOL_NAME,
  title: TOOL_TITLE,
  description: TOOL_DESCRIPTION,
  inputSchema: InputSchema,
  outputSchema: OutputSchema,
  annotations: TOOL_ANNOTATIONS,
  logic: withToolAuth(['cerata:status:read'], getStatusLogic),
  responseFormatter,
};
