import * as vscode from 'vscode';
import { spawn, execSync } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Result from a CLI command execution
 */
export interface CliResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

/**
 * JSON output from CLI commands
 */
export interface CliJsonOutput {
  success: boolean;
  data?: unknown;
  error?: string;
  tokens?: number;
  budget?: number;
  session?: {
    id: string;
    tokens: number;
    budget: number;
    created_at: string;
  };
}

/**
 * Locate the TokenCUNT CLI executable
 * Priority: 1) Custom path in config, 2) Bundled with extension, 3) PATH
 */
function findCliPath(): string | null {
  // Check custom path in configuration
  const config = vscode.workspace.getConfiguration('tokencunt');
  const customPath = config.get<string>('cliPath');
  
  if (customPath && fs.existsSync(customPath)) {
    return customPath;
  }

  // Check common locations
  const possiblePaths = [
    // pip installed
    'ts',
    'tokencunt',
    // Direct Python execution
    process.platform === 'win32' ? 'ts.exe' : 'ts',
    // Try finding in virtualenv if exists
    path.join(process.cwd(), '.venv', 'bin', process.platform === 'win32' ? 'ts.exe' : 'ts'),
  ];

  for (const cliPath of possiblePaths) {
    try {
      // Check if command exists
      execSync(cliPath, { stdio: 'ignore' });
      return cliPath;
    } catch {
      continue;
    }
  }

  return null;
}

/**
 * Run a TokenCUNT CLI command
 * @param args - Command arguments (e.g., ['analyze', '--file', 'test.py'])
 * @param options - Execution options
 * @returns Promise resolving to CLI result
 */
export async function runCliCommand(
  args: string[],
  options: {
    json?: boolean;
    timeout?: number;
  } = {}
): Promise<CliResult> {
  const { json = false, timeout = 30000 } = options;

  const cliPath = findCliPath();
  
  if (!cliPath) {
    return {
      stdout: '',
      stderr: 'TokenCUNT CLI not found. Please install with: pip install tokencunt',
      exitCode: 1
    };
  }

  // Add --json flag if requested and supported
  const finalArgs = json ? [...args, '--json'] : args;

  return new Promise((resolve) => {
    const stdout: string[] = [];
    const stderr: string[] = [];

    const child = spawn(cliPath, finalArgs, {
      shell: true,
      env: {
        ...process.env,
        // Pass VSCode config as env vars
        MINIMAX_API_KEY: vscode.workspace.getConfiguration('tokencunt').get<string>('apiKey') || process.env.MINIMAX_API_KEY || '',
        MINIMAX_GROUP_ID: vscode.workspace.getConfiguration('tokencunt').get<string>('groupId') || process.env.MINIMAX_GROUP_ID || '',
      }
    });

    child.stdout?.on('data', (data) => {
      stdout.push(data.toString());
    });

    child.stderr?.on('data', (data) => {
      stderr.push(data.toString());
    });

    const timeoutHandle = setTimeout(() => {
      child.kill();
      resolve({
        stdout: stdout.join(''),
        stderr: 'Command timed out',
        exitCode: 124
      });
    }, timeout);

    child.on('close', (code) => {
      clearTimeout(timeoutHandle);
      resolve({
        stdout: stdout.join(''),
        stderr: stderr.join(''),
        exitCode: code ?? 0
      });
    });

    child.on('error', (err) => {
      clearTimeout(timeoutHandle);
      resolve({
        stdout: '',
        stderr: err.message,
        exitCode: 1
      });
    });
  });
}

/**
 * Run CLI command and parse JSON output
 * @param args - Command arguments
 * @returns Parsed JSON output or null on error
 */
export async function runCliJsonCommand(args: string[]): Promise<CliJsonOutput | null> {
  const result = await runCliCommand(args, { json: true });
  
  if (result.exitCode !== 0 || result.stderr) {
    vscode.window.showErrorMessage(`TokenCUNT Error: ${result.stderr || 'Unknown error'}`);
    return null;
  }

  try {
    return JSON.parse(result.stdout) as CliJsonOutput;
  } catch {
    // If not valid JSON, return raw output wrapped
    return {
      success: true,
      data: result.stdout
    };
  }
}

/**
 * Get current session information from CLI
 * @returns Session data or null
 */
export async function getSessionInfo(): Promise<{ tokens: number; budget: number } | null> {
  const result = await runCliCommand(['session', 'list']);
  
  if (result.exitCode !== 0) {
    return null;
  }

  // Try to parse session info from output
  const output = result.stdout;
  const tokensMatch = output.match(/tokens[:\s]+(\d+)/i);
  const budgetMatch = output.match(/budget[:\s]+(\d+)/i);
  
  if (tokensMatch && budgetMatch) {
    return {
      tokens: parseInt(tokensMatch[1], 10),
      budget: parseInt(budgetMatch[1], 10)
    };
  }

  return null;
}
