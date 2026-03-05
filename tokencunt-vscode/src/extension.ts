import * as vscode from 'vscode';
import { getSessionInfo } from './cli';
import { createStatusBar, refreshStatusBar, updateStatusBar, resetStatusBar } from './statusbar';
import { registerHoverProvider } from './hover';
import { registerCommands } from './commands';
import { showSetupWebview, isSetupComplete } from './setup-webview';
import { checkBudgetAlert, resetAlerts, getThresholds } from './alerts';

// Track extension state
let statusBar: vscode.StatusBarItem;
let extensionContext: vscode.ExtensionContext;

/**
 * Activate the extension
 * This is called when VSCode loads the extension
 */
export function activate(context: vscode.ExtensionContext): void {
  extensionContext = context;
  
  // Initialize status bar
  statusBar = createStatusBar();
  
  // Register hover provider for token estimation
  const hoverDisposables = registerHoverProvider();
  if (hoverDisposables && 'hoverProvider' in hoverDisposables) {
    context.subscriptions.push(hoverDisposables.hoverProvider);
    context.subscriptions.push(hoverDisposables.sendToTokenCunt);
  }

  // Register all commands
  const commandDisposables = registerCommands(context);
  context.subscriptions.push(...commandDisposables);

  // Check for first-run and setup
  checkFirstRun(context);

  // Listen for configuration changes
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration('tokencunt')) {
        handleConfigurationChange();
      }
    })
  );

  // Update status bar and check budget
  updateWithBudgetCheck();
}

/**
 * Check for first-run and show welcome/setup
 */
async function checkFirstRun(context: vscode.ExtensionContext): Promise<void> {
  const config = vscode.workspace.getConfiguration('tokencunt');
  const autoShowSetup = config.get<boolean>('autoShowSetup') ?? true;
  
  if (autoShowSetup) {
    const setupComplete = await isSetupComplete();
    
    if (!setupComplete) {
      // First run - show setup wizard
      await showSetupWebview();
    }
  }
}

/**
 * Handle configuration changes
 */
function handleConfigurationChange(): void {
  // Refresh status bar when config changes
  updateWithBudgetCheck().catch(() => {
    // Silently fail
  });
}

/**
 * Update status bar and check budget alerts
 */
async function updateWithBudgetCheck(): Promise<void> {
  try {
    const config = vscode.workspace.getConfiguration('tokencunt');
    const budget = config.get<number>('budget') || 10000;
    
    const sessionInfo = await getSessionInfo();
    
    if (sessionInfo) {
      updateStatusBar(sessionInfo.tokens, budget);
      
      // Check for budget alerts
      checkBudgetAlert(sessionInfo.tokens, budget);
    } else {
      resetStatusBar();
    }
  } catch (error) {
    // If we can't get session info, just show initial state
    const config = vscode.workspace.getConfiguration('tokencunt');
    const budget = config.get<number>('budget') || 10000;
    resetStatusBar();
  }
}

/**
 * Deactivate the extension
 * Cleanup resources
 */
export function deactivate(): void {
  // Status bar will be disposed by VSCode when extension deactivates
  // All subscriptions in context.subscriptions are automatically disposed
  resetAlerts();
}
