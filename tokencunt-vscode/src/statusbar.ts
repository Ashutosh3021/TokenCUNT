import * as vscode from 'vscode';
import { getSessionInfo } from './cli';

/**
 * Token budget thresholds for color coding
 */
const THRESHOLD_WARNING = 50;  // Yellow
const THRESHOLD_CRITICAL = 80; // Red

/**
 * Create and return the status bar item
 */
let statusBarItem: vscode.StatusBarItem;

export function createStatusBar(): vscode.StatusBarItem {
  statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    100
  );
  
  statusBarItem.text = '⚡ TokenCUNT';
  statusBarItem.command = 'tokencunt.showQuickPick';
  statusBarItem.tooltip = 'TokenCUNT: Click to view options';
  statusBarItem.show();
  
  return statusBarItem;
}

/**
 * Update the status bar with current token count
 * @param tokens - Current token count
 * @param budget - Budget limit
 */
export function updateStatusBar(tokens: number, budget: number): void {
  if (!statusBarItem) {
    createStatusBar();
  }

  const percent = budget > 0 ? Math.round((tokens / budget) * 100) : 0;
  
  // Update text and tooltip
  statusBarItem.text = `⚡ ${tokens.toLocaleString()} / ${budget.toLocaleString()}`;
  statusBarItem.tooltip = `TokenCUNT: ${tokens.toLocaleString()} / ${budget.toLocaleString()} tokens (${percent}%)`;
  
  // Color coding based on budget usage
  if (percent >= THRESHOLD_CRITICAL) {
    statusBarItem.color = new vscode.ThemeColor('errorForeground');
    statusBarItem.icon = 'warning';
  } else if (percent >= THRESHOLD_WARNING) {
    statusBarItem.color = new vscode.ThemeColor('warningForeground');
    statusBarItem.icon = 'zap';
  } else {
    statusBarItem.color = undefined;
    statusBarItem.icon = 'zap';
  }
}

/**
 * Reset status bar to initial state
 */
export function resetStatusBar(): void {
  if (!statusBarItem) {
    createStatusBar();
  }
  
  const config = vscode.workspace.getConfiguration('tokencunt');
  const budget = config.get<number>('budget') || 10000;
  
  statusBarItem.text = `⚡ 0 / ${budget.toLocaleString()}`;
  statusBarItem.tooltip = 'TokenCUNT: No active session';
  statusBarItem.color = undefined;
  statusBarItem.icon = 'zap';
}

/**
 * Get the status bar item
 */
export function getStatusBar(): vscode.StatusBarItem | undefined {
  return statusBarItem;
}

/**
 * Refresh status bar from CLI session info
 */
export async function refreshStatusBar(): Promise<void> {
  try {
    const sessionInfo = await getSessionInfo();
    const config = vscode.workspace.getConfiguration('tokencunt');
    const budget = config.get<number>('budget') || 10000;
    
    if (sessionInfo) {
      updateStatusBar(sessionInfo.tokens, budget);
    } else {
      resetStatusBar();
    }
  } catch (error) {
    // On error, show unconfigured state
    const config = vscode.workspace.getConfiguration('tokencunt');
    const budget = config.get<number>('budget') || 10000;
    updateStatusBar(0, budget);
  }
}
