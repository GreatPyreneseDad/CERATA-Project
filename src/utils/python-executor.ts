/**
 * @fileoverview Python subprocess execution utility for nematocyst invocation
 * @module utils/python-executor
 */

import { spawn } from 'child_process';
import { JsonRpcErrorCode, McpError } from '@/types-global/errors.js';
import type { RequestContext } from './internal/requestContext.js';
import { logger } from './internal/logger.js';

export interface PythonExecutionOptions {
  /**
   * Python script path (absolute or relative to project root)
   */
  scriptPath: string;

  /**
   * JSON input to send via stdin
   */
  input: Record<string, unknown>;

  /**
   * Timeout in milliseconds (default: 30000)
   */
  timeout?: number;

  /**
   * Working directory (default: integrations/)
   */
  cwd?: string;

  /**
   * Python interpreter to use (default: 'python3')
   */
  pythonPath?: string;
}

export interface PythonExecutionResult<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  errorType?: string;
  stdout: string;
  stderr: string;
}

/**
 * Execute Python script with JSON I/O via stdin/stdout
 *
 * @param options - Execution options
 * @param context - Request context for logging
 * @returns Promise resolving to execution result
 */
export async function executePythonScript<T = unknown>(
  options: PythonExecutionOptions,
  context: RequestContext,
): Promise<PythonExecutionResult<T>> {
  const {
    scriptPath,
    input,
    timeout = 30000,
    cwd,
    pythonPath = 'python3',
  } = options;

  return new Promise((resolve, reject) => {
    logger.debug('Executing Python script', {
      ...context,
      scriptPath,
      timeout,
    });

    const child = spawn(pythonPath, [scriptPath], {
      cwd,
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';
    let timedOut = false;

    // Set timeout
    const timeoutHandle = setTimeout(() => {
      timedOut = true;
      child.kill('SIGTERM');
    }, timeout);

    // Collect stdout
    child.stdout.on('data', (data: Buffer) => {
      stdout += data.toString();
    });

    // Collect stderr
    child.stderr.on('data', (data: Buffer) => {
      stderr += data.toString();
    });

    // Handle completion
    child.on('close', (code: number | null) => {
      clearTimeout(timeoutHandle);

      if (timedOut) {
        logger.error('Python script execution timed out', {
          ...context,
          scriptPath,
          timeout,
        });
        reject(
          new McpError(
            JsonRpcErrorCode.Timeout,
            `Python script timed out after ${timeout}ms`,
            { scriptPath, timeout },
          ),
        );
        return;
      }

      if (code !== 0) {
        logger.error('Python script failed', {
          ...context,
          scriptPath,
          code,
          stderr: stderr.substring(0, 500),
        });
        reject(
          new McpError(
            JsonRpcErrorCode.InternalError,
            `Python script exited with code ${code}: ${stderr.substring(0, 200)}`,
            { scriptPath, code, stderr },
          ),
        );
        return;
      }

      // Parse JSON output
      try {
        const result = JSON.parse(stdout) as PythonExecutionResult<T>;

        if (result.success) {
          logger.debug('Python script succeeded', {
            ...context,
            scriptPath,
          });
          resolve({
            ...result,
            stdout,
            stderr,
          });
        } else {
          logger.warning('Python script returned error', {
            ...context,
            scriptPath,
            error: result.error,
            errorType: result.errorType,
          });
          resolve({
            ...result,
            stdout,
            stderr,
          });
        }
      } catch (parseError) {
        logger.error('Failed to parse Python script output', {
          ...context,
          scriptPath,
          parseError:
            parseError instanceof Error
              ? parseError.message
              : String(parseError),
          stdout: stdout.substring(0, 500),
        });
        reject(
          new McpError(
            JsonRpcErrorCode.InternalError,
            'Failed to parse Python script output as JSON',
            {
              scriptPath,
              parseError: String(parseError),
              stdout: stdout.substring(0, 200),
            },
          ),
        );
      }
    });

    // Handle errors
    child.on('error', (err: Error) => {
      clearTimeout(timeoutHandle);
      logger.error('Failed to spawn Python process', {
        ...context,
        scriptPath,
        error: err.message,
      });
      reject(
        new McpError(
          JsonRpcErrorCode.InternalError,
          `Failed to spawn Python process: ${err.message}`,
          { scriptPath, error: err.message },
        ),
      );
    });

    // Send input via stdin
    try {
      child.stdin.write(JSON.stringify(input));
      child.stdin.end();
    } catch (writeError) {
      clearTimeout(timeoutHandle);
      child.kill();
      logger.error('Failed to write to Python stdin', {
        ...context,
        scriptPath,
        error:
          writeError instanceof Error ? writeError.message : String(writeError),
      });
      reject(
        new McpError(
          JsonRpcErrorCode.InternalError,
          'Failed to write input to Python script',
          { scriptPath, error: String(writeError) },
        ),
      );
    }
  });
}
