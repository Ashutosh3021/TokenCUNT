import * as vscode from 'vscode';
import { getSessionInfo } from './cli';
import { createStatusBar, refreshStatusBar } from './statusbar';
import { registerHoverProvider } from './hover';
import { registerCommands } from './commands';

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

  // Show welcome message
  checkAndShowWelcome();

  // Update status bar with current session info
  refreshStatusBar().catch(() => {
    // Silently fail if session info unavailable
  });
}

/**
 * Check for first-run and show welcome/setup
 */
async function checkAndShowWelcome(): Promise<void> {
  const config = vscode.workspace.getConfiguration('tokencunt');
  const autoShowSetup = config.get<boolean>('autoShowSetup') ?? true;
  
  if (autoShowSetup) {
    const apiKey = config.get<string>('apiKey');
    
    if (!apiKey) {
      // First run - show welcome and prompt for setup
      const response = await vscode.window.showInformationMessage(
        'TokenCUNT v0.1.0 activated! Would you like to configure your API key?',
        'Configure Now',
        'Later'
      );
      
      if (response === 'Configure Now') {
        vscode.commands.executeCommand('tokencunt.configureApiKey');
      }
    }
  }
}

/**
 * Deactivate the extension
 * Cleanup resources
 */
export function deactivate(): void {
  // Status bar will be disposed by VSCode when extension deactivates
  // All subscriptions in context.subscriptions are automatically disposed
}

/**
 * Update the status bar with current session info
 */
async function updateStatusBar(): Promise<void> {
  try {
    const sessionInfo = await getSessionInfo();
    const config = vscode.workspace.getConfiguration('tokencunt');
    const budget = config.get<number>('budget') || 10000;
    
    if (sessionInfo) {
      const percent = Math.round((sessionInfo.tokens / budget) * 100);
      statusBar.text = `⚡ ${sessionInfo.tokens.toLocaleString()} / ${budget.toLocaleString()}`;
      statusBar.tooltip = `TokenCUNT: ${sessionInfo.tokens} / ${budget} tokens (${percent}%)`;
      
      // Color coding
      if (percent > 80) {
        statusBar.color = new vscode.ThemeColor('errorForeground');
      } else if (percent > 50) {
        statusBar.color = new vscode.ThemeColor('warningForeground');
      } else {
        statusBar.color = undefined;
      }
    } else {
      statusBar.text = `⚡ 0 / ${budget.toLocaleString()}`;
      statusBar.tooltip = `TokenCUNT: No active session`;
    }
  } catch (error) {
    statusBar.text = '⚡ TokenCUNT';
    statusBar.tooltip = 'TokenCUNT: Click to configure';
  }
}
