/**
 * @fileoverview CERATA hunt-repo tool - Hunts GitHub repositories with Rose Glass perception
 * @module src/mcp-server/tools/definitions/cerata-hunt-repo.tool
 */

import type { ContentBlock } from '@modelcontextprotocol/sdk/types.js';
import { inject, injectable } from 'tsyringe';
import { z } from 'zod';

import { RoseGlassService } from '@/container/tokens.js';
import type { RoseGlassService as RoseGlassServiceClass } from '@/services/rose-glass/rose-glass.service.js';
import type { RawDimensions } from '@/services/rose-glass/types.js';
import type { StorageService } from '@/storage/core/StorageService.js';
import { StorageService as StorageServiceToken } from '@/container/tokens.js';
import { type ToolDefinition } from '../utils/toolDefinition.js';
import { JsonRpcErrorCode, McpError } from '@/types-global/errors.js';
import type { RequestContext } from '@/utils/index.js';
import { fetchWithTimeout, markdown } from '@/utils/index.js';

// ============================================================================
// Tool Metadata
// ============================================================================
const TOOL_NAME = 'cerata_hunt_repo';
const TOOL_TITLE = 'Hunt Repository';
const TOOL_DESCRIPTION = `Hunt a GitHub repository and perceive it through Rose Glass.

Analyzes repository structure, metadata, and code patterns using the Rose Glass perception framework. Returns a coherence assessment with detected patterns and warnings.

**Returns:**
- Repository metadata (stars, forks, language, age)
- Rose Glass perception report (dimensions, coherence, patterns)
- Hunt timestamp and lens used
- Storage location in hunt history`;

const TOOL_ANNOTATIONS = {
  readOnlyHint: false, // Writes to hunt history
  idempotentHint: false,
};

// ============================================================================
// Input/Output Schemas
// ============================================================================
const InputSchema = z.object({
  repo: z
    .string()
    .describe(
      'GitHub repository as "owner/name" or full URL (e.g., "facebook/react" or "https://github.com/facebook/react")',
    ),
  lens: z
    .string()
    .optional()
    .describe(
      'Rose Glass lens to use for perception (defaults to "code-analysis")',
    ),
});

type Input = z.infer<typeof InputSchema>;

const OutputSchema = z.object({
  success: z.boolean().describe('Whether the hunt succeeded'),
  repo: z.object({
    owner: z.string().describe('Repository owner'),
    name: z.string().describe('Repository name'),
    fullName: z.string().describe('Full repository name (owner/name)'),
    url: z.string().describe('GitHub URL'),
    description: z.string().nullable().describe('Repository description'),
    stars: z.number().describe('Star count'),
    forks: z.number().describe('Fork count'),
    language: z.string().nullable().describe('Primary language'),
    createdAt: z.string().describe('Creation date'),
    updatedAt: z.string().describe('Last update date'),
    openIssues: z.number().describe('Open issue count'),
    hasWiki: z.boolean().describe('Has wiki'),
    hasTests: z.boolean().describe('Detected test presence'),
  }),
  perception: z.object({
    lens: z.string().describe('Lens used for perception'),
    dimensions: z.object({
      psi: z.number().describe('Ψ - Internal consistency (0-1)'),
      rho: z.number().describe('ρ - Accumulated wisdom (0-1)'),
      q: z.number().describe('q - Activation energy (0-1)'),
      f: z.number().describe('f - Social belonging (0-1)'),
      tau: z.number().describe('τ - Temporal depth (0-1)'),
      lambda: z.number().describe('λ - Lens interference (0-1)'),
    }),
    coherence: z.number().describe('Overall coherence (0-4 scale)'),
    qOptimized: z.number().describe('Biologically optimized q'),
    confidence: z.enum(['low', 'medium', 'high']).describe('Confidence level'),
    patterns: z.array(z.string()).describe('Detected patterns'),
    warnings: z.array(z.string()).describe('Perception warnings'),
  }),
  huntId: z.string().describe('Unique hunt identifier'),
  timestamp: z.string().describe('Hunt timestamp (ISO 8601)'),
});

type Output = z.infer<typeof OutputSchema>;

// ============================================================================
// Storage Keys
// ============================================================================
const STORAGE_KEYS = {
  huntHistoryPrefix: 'cerata:hunt:',
  instanceStats: 'cerata:instance:stats',
} as const;

// ============================================================================
// GitHub API Types
// ============================================================================
interface GitHubRepo {
  id: number;
  name: string;
  full_name: string;
  owner: { login: string };
  html_url: string;
  description: string | null;
  stargazers_count: number;
  forks_count: number;
  language: string | null;
  created_at: string;
  updated_at: string;
  open_issues_count: number;
  has_wiki: boolean;
  topics?: string[];
}

// ============================================================================
// Tool Logic Implementation
// ============================================================================
@injectable()
class CerataHuntRepoLogic {
  constructor(
    @inject(StorageServiceToken) private storage: StorageService,
    @inject(RoseGlassService) private roseGlass: RoseGlassServiceClass,
  ) {}

  async execute(input: Input, context: RequestContext): Promise<Output> {
    const { repo, lens } = input;

    // Parse repository identifier
    const { owner, name } = this.parseRepoIdentifier(repo);

    // Fetch repository metadata from GitHub
    const repoData = await this.fetchGitHubRepo(owner, name);

    // Extract Rose Glass dimensions from repository data
    const dimensions = this.extractDimensions(repoData);

    // Apply Rose Glass perception
    const perception = this.roseGlass.perceive(dimensions, lens);

    // Generate hunt ID and store in history
    const huntId = crypto.randomUUID();
    const timestamp = new Date().toISOString();

    const huntRecord = {
      huntId,
      timestamp,
      repo: {
        owner,
        name,
        fullName: `${owner}/${name}`,
        url: repoData.html_url,
      },
      perception,
      dimensions,
    };

    // Store hunt in history (use 'cerata-system' tenant for instance-level data)
    const systemContext = { ...context, tenantId: 'cerata-system' };
    await this.storage.set(
      `${STORAGE_KEYS.huntHistoryPrefix}${huntId}`,
      huntRecord,
      systemContext,
    );

    // Update instance stats
    await this.incrementHuntCount(systemContext);

    return {
      success: true,
      repo: {
        owner,
        name,
        fullName: `${owner}/${name}`,
        url: repoData.html_url,
        description: repoData.description,
        stars: repoData.stargazers_count,
        forks: repoData.forks_count,
        language: repoData.language,
        createdAt: repoData.created_at,
        updatedAt: repoData.updated_at,
        openIssues: repoData.open_issues_count,
        hasWiki: repoData.has_wiki,
        hasTests: this.detectTests(repoData),
      },
      perception: {
        lens: perception.lens,
        dimensions: perception.dimensions,
        coherence: perception.coherence,
        qOptimized: perception.qOptimized,
        confidence: perception.confidence,
        patterns: perception.patterns,
        warnings: perception.warnings,
      },
      huntId,
      timestamp,
    };
  }

  /**
   * Parse repository identifier from various formats
   */
  private parseRepoIdentifier(repo: string): { owner: string; name: string } {
    // Handle full URL: https://github.com/owner/name
    if (repo.startsWith('http://') || repo.startsWith('https://')) {
      const match = repo.match(/github\.com\/([^/]+)\/([^/]+)/);
      if (!match) {
        throw new McpError(
          JsonRpcErrorCode.InvalidParams,
          `Invalid GitHub URL: ${repo}`,
        );
      }
      return { owner: match[1], name: match[2] };
    }

    // Handle owner/name format
    const parts = repo.split('/');
    if (parts.length !== 2) {
      throw new McpError(
        JsonRpcErrorCode.InvalidParams,
        `Invalid repository format. Use "owner/name" or full GitHub URL`,
      );
    }

    return { owner: parts[0], name: parts[1] };
  }

  /**
   * Fetch repository metadata from GitHub API
   */
  private async fetchGitHubRepo(
    owner: string,
    name: string,
  ): Promise<GitHubRepo> {
    const url = `https://api.github.com/repos/${owner}/${name}`;

    // Get optional GitHub token from env (allows higher rate limits)
    const token = process.env.GITHUB_TOKEN;
    const headers: Record<string, string> = {
      Accept: 'application/vnd.github.v3+json',
      'User-Agent': 'CERATA-MCP-Server',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetchWithTimeout(url, {
        method: 'GET',
        headers,
        timeout: 10000,
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new McpError(
            JsonRpcErrorCode.InvalidParams,
            `Repository not found: ${owner}/${name}`,
          );
        }
        if (response.status === 403) {
          throw new McpError(
            JsonRpcErrorCode.RateLimited,
            'GitHub API rate limit exceeded. Set GITHUB_TOKEN for higher limits.',
          );
        }
        throw new McpError(
          JsonRpcErrorCode.InternalError,
          `GitHub API error: ${response.status} ${response.statusText}`,
        );
      }

      return (await response.json()) as GitHubRepo;
    } catch (error) {
      if (error instanceof McpError) throw error;
      throw new McpError(
        JsonRpcErrorCode.InternalError,
        `Failed to fetch repository: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }

  /**
   * Extract Rose Glass dimensions from repository data
   */
  private extractDimensions(repo: GitHubRepo): RawDimensions {
    // Calculate repository age in days
    const createdDate = new Date(repo.created_at);
    const now = new Date();
    const ageInDays =
      (now.getTime() - createdDate.getTime()) / (1000 * 60 * 60 * 24);
    const ageInYears = ageInDays / 365;

    // Ψ (psi) - Internal consistency
    // Based on update recency and issue ratio
    const daysSinceUpdate =
      (now.getTime() - new Date(repo.updated_at).getTime()) /
      (1000 * 60 * 60 * 24);
    const updateRecency = Math.max(0, 1 - daysSinceUpdate / 365); // 0-1, recent = high
    const issueRatio = repo.open_issues_count / (repo.stargazers_count + 1);
    const issueHealth = Math.max(0, 1 - Math.min(1, issueRatio)); // Low issues = high health
    const psi = updateRecency * 0.6 + issueHealth * 0.4;

    // ρ (rho) - Accumulated wisdom (battle-tested)
    // Based on age and activity indicators
    const maturity = Math.min(1, ageInYears / 5); // Mature after 5 years
    const activitySignal = Math.min(1, repo.stargazers_count / 10000); // Stars as proxy
    const rho = maturity * 0.7 + activitySignal * 0.3;

    // q - Activation energy
    // Based on recent activity and community engagement
    const recentActivity = Math.min(1, 1 / (daysSinceUpdate + 1)); // More recent = higher
    const communitySize = Math.min(
      1,
      (repo.stargazers_count + repo.forks_count) / 5000,
    );
    const q = recentActivity * 0.5 + communitySize * 0.5;

    // f - Social belonging (ecosystem fit)
    // Based on forks, stars, and language ecosystem
    const forkRatio = repo.forks_count / (repo.stargazers_count + 1);
    const forkHealth = Math.min(1, forkRatio * 5); // Good fork ratio suggests integration
    const hasLanguage = repo.language ? 0.3 : 0;
    const hasWiki = repo.has_wiki ? 0.2 : 0;
    const popularity = Math.min(1, repo.stargazers_count / 50000);
    const f = Math.min(
      1,
      forkHealth * 0.3 + hasLanguage + hasWiki + popularity * 0.2,
    );

    return { psi, rho, q, f };
  }

  /**
   * Detect if repository likely has tests
   */
  private detectTests(repo: GitHubRepo): boolean {
    // Heuristic: repos with good star count and active maintenance likely have tests
    // This is a placeholder - real implementation would fetch repo contents
    return repo.stargazers_count > 100 && repo.open_issues_count < 100;
  }

  /**
   * Increment hunt count in instance stats
   */
  private async incrementHuntCount(context: RequestContext): Promise<void> {
    const stats = await this.storage.get<{ huntCount: number }>(
      STORAGE_KEYS.instanceStats,
      context,
    );

    const newStats = {
      huntCount: (stats?.huntCount ?? 0) + 1,
      lastHuntAt: new Date().toISOString(),
    };

    await this.storage.set(STORAGE_KEYS.instanceStats, newStats, context);
  }
}

// ============================================================================
// Response Formatter
// ============================================================================
const responseFormatter = (result: Output): ContentBlock[] => {
  const md = markdown()
    .h1('🎯 Hunt Report: ' + result.repo.fullName)
    .h2('Repository Overview')
    .keyValue('URL', result.repo.url)
    .keyValue('Description', result.repo.description ?? '*No description*')
    .keyValue('Language', result.repo.language ?? '*Unknown*')
    .keyValue('Stars', result.repo.stars.toLocaleString())
    .keyValue('Forks', result.repo.forks.toLocaleString())
    .keyValue('Open Issues', result.repo.openIssues.toLocaleString())
    .keyValue('Created', new Date(result.repo.createdAt).toLocaleDateString())
    .keyValue(
      'Last Updated',
      new Date(result.repo.updatedAt).toLocaleDateString(),
    )
    .blank()
    .h2('👁️ Rose Glass Perception')
    .keyValue('Lens', result.perception.lens)
    .keyValue('Coherence', `${result.perception.coherence.toFixed(2)} / 4.00`)
    .keyValue('Confidence', result.perception.confidence)
    .blank()
    .h3('Dimensions')
    .keyValue(
      'Ψ (Internal Consistency)',
      result.perception.dimensions.psi.toFixed(3),
    )
    .keyValue(
      'ρ (Accumulated Wisdom)',
      result.perception.dimensions.rho.toFixed(3),
    )
    .keyValue(
      'q (Activation Energy)',
      result.perception.dimensions.q.toFixed(3),
    )
    .keyValue('q_opt (Optimized)', result.perception.qOptimized.toFixed(3))
    .keyValue('f (Social Belonging)', result.perception.dimensions.f.toFixed(3))
    .keyValue('τ (Temporal Depth)', result.perception.dimensions.tau.toFixed(3))
    .keyValue(
      'λ (Lens Interference)',
      result.perception.dimensions.lambda.toFixed(3),
    );

  if (result.perception.patterns.length > 0) {
    md.blank().h3('Detected Patterns').list(result.perception.patterns);
  }

  if (result.perception.warnings.length > 0) {
    md.blank().h3('⚠️ Warnings').list(result.perception.warnings);
  }

  md.blank()
    .h2('Hunt Metadata')
    .keyValue('Hunt ID', result.huntId)
    .keyValue('Timestamp', new Date(result.timestamp).toLocaleString())
    .keyValue('Storage Key', `cerata:hunt:${result.huntId}`);

  return [{ type: 'text', text: md.build() }];
};

// ============================================================================
// Tool Definition Export
// ============================================================================
export const cerataHuntRepoTool: ToolDefinition<
  typeof InputSchema,
  typeof OutputSchema
> = {
  name: TOOL_NAME,
  title: TOOL_TITLE,
  description: TOOL_DESCRIPTION,
  inputSchema: InputSchema,
  outputSchema: OutputSchema,
  annotations: TOOL_ANNOTATIONS,
  logic: async (input, appContext, _sdkContext) => {
    const logic = new CerataHuntRepoLogic(
      appContext.container.resolve(StorageServiceToken),
      appContext.container.resolve(RoseGlassService),
    );
    return await logic.execute(input, appContext);
  },
  responseFormatter,
};
