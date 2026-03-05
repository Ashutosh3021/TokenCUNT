import * as vscode from 'vscode';

/**
 * Budget alert levels
 */
export type AlertLevel = 'info' | 'warning' | 'critical';

/**
 * Budget thresholds
 */
const THRESHOLD_INFO = 50;     // 50% - Info
const THRESHOLD_WARNING = 80;  // 80% - Warning  
const THRESHOLD_CRITICAL = 95; // 95% - Critical

/**
 * Track last alert time to debounce
 */
let lastAlertTime = 0;
const ALERT_DEBOUNCE_MS = 60000; // 1 minute debounce

/**
 * Track last alert level to avoid duplicates
 */
let lastAlertLevel: AlertLevel | null = null;

/**
 * Check if budget alert should be triggered
 * @param tokens - Current token count
 * @param budget - Budget limit
 */
export function checkBudgetAlert(tokens: number, budget: number): void {
  if (budget <= 0) { return; }
  
  const percent = Math.round((tokens / budget) * 100);
  
  // Determine alert level
  let level: AlertLevel | null = null;
  
  if (percent >= THRESHOLD_CRITICAL) {
    level = 'critical';
  } else if (percent >= THRESHOLD_WARNING) {
    level = 'warning';
  } else if (percent >= THRESHOLD_INFO) {
    level = 'info';
  }
  
  // Only show alert if:
  // 1. There's a new level to show
  // 2. Enough time has passed (debounce)
  // 3. It's a higher priority than the last alert
  const now = Date.now();
  const priority = { critical: 3, warning: 2, info: 1 };
  
  if (level && (
    (lastAlertLevel === null || priority[level] > priority[lastAlertLevel]) &&
    (now - lastAlertTime > ALERT_DEBOUNCE_MS)
  )) {
    showBudgetWarning(level, tokens, budget);
    lastAlertTime = now;
    lastAlertLevel = level;
  }
}

/**
 * Show budget warning notification
 * @param level - Alert level
 * @param tokens - Current tokens
 * @param budget - Budget limit
 */
export function showBudgetWarning(
  level: AlertLevel, 
  tokens: number, 
  budget: number
): void {
  const percent = Math.round((tokens / budget) * 100);
  
  let message: string;
  let alertType: 'info' | 'warning' | 'error';
  
  switch (level) {
    case 'info':
      message = `TokenCUNT: ${percent}% of budget used (${tokens.toLocaleString()}/${budget.toLocaleString()})`;
      alertType = 'info';
      break;
      
    case 'warning':
      message = `TokenCUNT: Approaching budget limit - ${percent}% used`;
      alertType = 'warning';
      break;
      
    case 'critical':
      message = `TokenCUNT: Budget nearly exhausted! ${percent}% used`;
      alertType = 'error';
      break;
  }
  
  // Show appropriate VSCode notification
  switch (alertType) {
    case 'info':
      vscode.window.showInformationMessage(message);
      break;
    case 'warning':
      vscode.window.showWarningMessage(message);
      break;
    case 'error':
      vscode.window.showErrorMessage(message);
      break;
  }
}

/**
 * Reset alert state (e.g., when session is cleared)
 */
export function resetAlerts(): void {
  lastAlertTime = 0;
  lastAlertLevel = null;
}

/**
 * Get current alert thresholds
 */
export function getThresholds(): { info: number; warning: number; critical: number } {
  return {
    info: THRESHOLD_INFO,
    warning: THRESHOLD_WARNING,
    critical: THRESHOLD_CRITICAL
  };
}

/**
 * Check budget and show alert if needed
 * This is the main entry point called from status bar updates
 */
export async function checkAndAlert(): Promise<void> {
  try {
    const config = vscode.workspace.getConfiguration('tokencunt');
    const budget = config.get<number>('budget') || 10000;
    
    // Try to get session info
    const { getSessionInfo } = await import('./cli');
    const sessionInfo = await getSessionInfo();
    
    if (sessionInfo) {
      checkBudgetAlert(sessionInfo.tokens, budget);
    }
  } catch (error) {
    // Silently fail - alerts are non-critical
  }
}
