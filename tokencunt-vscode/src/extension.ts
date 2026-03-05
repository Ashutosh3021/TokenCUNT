import * as vscode from 'vscode';
import { runCliCommand, runCliJsonCommand, getSessionInfo } from './cli';

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
  statusBar = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    100
  );
  statusBar.text = '⚡ TokenCUNT';
  statusBar.command = 'tokencunt.showQuickPick';
  statusBar.tooltip = 'TokenCUNT: Click to view options';
  statusBar.show();

  // Register all commands
  registerCommands(context);

  // Show welcome message
  vscode.window.showInformationMessage(
    'TokenCUNT v0.1.0 activated! Run "TokenCUNT: Configure API Key" to get started.'
  );

  // Update status bar with current session info
  updateStatusBar();
}

/**
 * Deactivate the extension
 * Cleanup resources
 */
export function deactivate(): void {
  if (statusBar) {
    statusBar.dispose();
  }
}

/**
 * Register all TokenCUNT commands
 */
function registerCommands(context: vscode.ExtensionContext): void {
  // Category A - Mirror CLI commands
  context.subscriptions.push(
    vscode.commands.registerCommand('tokencunt.analyzeFile', async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage('No active editor');
        return;
      }

      const selection = editor.selection;
      const selectedText = editor.document.getText(selection);
      
      if (!selectedText) {
        vscode.window.showWarningMessage('No text selected');
        return;
      }

      // Create temp file for analysis
      const tempFile = path.join(require('os').tmpdir(), `tokencunt_analysis_${Date.now()}.txt`);
      require('fs').writeFileSync(tempFile, selectedText);

      const result = await runCliCommand(['analyze', '--file', tempFile]);
      
      if (result.exitCode === 0) {
        vscode.window.showInformationMessage('Analysis complete');
        // Show output in output channel
        const outputChannel = vscode.window.createOutputChannel('TokenCUNT Analysis');
        outputChannel.append(result.stdout);
        outputChannel.show();
      } else {
        vscode.window.showErrorMessage(`Analysis failed: ${result.stderr}`);
      }
    }),

    vscode.commands.registerCommand('tokencunt.showReport', async () => {
      const result = await runCliCommand(['report']);
      
      if (result.exitCode === 0) {
        const outputChannel = vscode.window.createOutputChannel('TokenCUNT Report');
        outputChannel.append(result.stdout);
        outputChannel.show();
      } else {
        vscode.window.showErrorMessage(`Report failed: ${result.stderr}`);
      }
    }),

    vscode.commands.registerCommand('tokencunt.ask', async () => {
      const editor = vscode.window.activeTextEditor;
      const selectedText = editor?.selection
        ? editor.document.getText(editor.selection)
        : '';

      const prompt = await vscode.window.showInputBox({
        prompt: 'Enter your question for TokenCUNT',
        value: selectedText || ''
      });

      if (!prompt) { return; }

      const result = await runCliCommand(['ask', prompt]);

      if (result.exitCode === 0) {
        const outputChannel = vscode.window.createOutputChannel('TokenCUNT Response');
        outputChannel.append(result.stdout);
        outputChannel.show();
      } else {
        vscode.window.showErrorMessage(`Ask failed: ${result.stderr}`);
      }
    })
  );

  // Category B - Quick Actions
  context.subscriptions.push(
    vscode.commands.registerCommand('tokencunt.newSession', async () => {
      const result = await runCliCommand(['session', 'new']);
      
      if (result.exitCode === 0) {
        vscode.window.showInformationMessage('New session created');
        updateStatusBar();
      } else {
        vscode.window.showErrorMessage(`Failed to create session: ${result.stderr}`);
      }
    }),

    vscode.commands.registerCommand('tokencunt.setBudget', async () => {
      const budgetStr = await vscode.window.showInputBox({
        prompt: 'Enter token budget',
        validateInput: (value: string) => {
          const num = parseInt(value, 10);
          return (num > 0 && num <= 1000000) ? null : 'Enter a number between 1 and 1,000,000';
        }
      });

      if (!budgetStr) { return; }

      const budget = parseInt(budgetStr, 10);
      const config = vscode.workspace.getConfiguration('tokencunt');
      await config.update('budget', budget, vscode.ConfigurationTarget.Global);
      
      vscode.window.showInformationMessage(`Budget set to ${budget.toLocaleString()} tokens`);
      updateStatusBar();
    }),

    vscode.commands.registerCommand('tokencunt.clearSession', async () => {
      const result = await runCliCommand(['session', 'clear']);
      
      if (result.exitCode === 0) {
        vscode.window.showInformationMessage('Session cleared');
        updateStatusBar();
      } else {
        vscode.window.showErrorMessage(`Failed to clear session: ${result.stderr}`);
      }
    })
  );

  // Category C - Settings
  context.subscriptions.push(
    vscode.commands.registerCommand('tokencunt.configureApiKey', async () => {
      const apiKey = await vscode.window.showInputBox({
        prompt: 'Enter your MiniMax API Key',
        password: true
      });

      if (!apiKey) { return; }

      const config = vscode.workspace.getConfiguration('tokencunt');
      await config.update('apiKey', apiKey, vscode.ConfigurationTarget.Global);
      
      vscode.window.showInformationMessage('API Key configured');
    }),

    vscode.commands.registerCommand('tokencunt.configureModel', async () => {
      const model = await vscode.window.showQuickPick(
        ['abab6.5-chat', 'abab6.5s-chat', 'abab5.5-chat'],
        { placeHolder: 'Select model' }
      );

      if (!model) { return; }

      const config = vscode.workspace.getConfiguration('tokencunt');
      await config.update('model', model, vscode.ConfigurationTarget.Global);
      
      vscode.window.showInformationMessage(`Model set to ${model}`);
    }),

    vscode.commands.registerCommand('tokencunt.viewSettings', async () => {
      const config = vscode.workspace.getConfiguration('tokencunt');
      const settings = {
        model: config.get('model'),
        budget: config.get('budget'),
        autoShowSetup: config.get('autoShowSetup'),
        cliPath: config.get('cliPath')
      };

      const outputChannel = vscode.window.createOutputChannel('TokenCUNT Settings');
      outputChannel.appendLine('Current TokenCUNT Settings:');
      outputChannel.appendLine(JSON.stringify(settings, null, 2));
      outputChannel.show();
    })
  );
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

// Import path for temp file
import * as path from 'path';
