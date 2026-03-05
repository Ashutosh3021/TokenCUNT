import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { runCliCommand, runCliJsonCommand, getSessionInfo } from './cli';
import { createStatusBar, updateStatusBar, resetStatusBar, refreshStatusBar } from './statusbar';

/**
 * Register all TokenCUNT commands
 * Returns disposable for cleanup
 */
export function registerCommands(context: vscode.ExtensionContext): vscode.Disposable[] {
  const disposables: vscode.Disposable[] = [];

  // ===== Category A: Mirror CLI Commands =====
  
  // Analyze File
  disposables.push(
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
      const tempFile = path.join(
        require('os').tmpdir(),
        `tokencunt_analysis_${Date.now()}.txt`
      );
      
      try {
        fs.writeFileSync(tempFile, selectedText, 'utf-8');
        vscode.window.showInformationMessage('Analyzing selected text...');

        const result = await runCliCommand(['analyze', '--file', tempFile]);
        
        if (result.exitCode === 0) {
          const outputChannel = vscode.window.createOutputChannel('TokenCUNT Analysis');
          outputChannel.append(result.stdout);
          outputChannel.show();
          
          // Refresh status bar after analysis
          await refreshStatusBar();
        } else {
          vscode.window.showErrorMessage(`Analysis failed: ${result.stderr}`);
        }
      } finally {
        try { fs.unlinkSync(tempFile); } catch { /* ignore */ }
      }
    })
  );

  // Show Report
  disposables.push(
    vscode.commands.registerCommand('tokencunt.showReport', async () => {
      const result = await runCliCommand(['report']);
      
      if (result.exitCode === 0) {
        const outputChannel = vscode.window.createOutputChannel('TokenCUNT Report');
        outputChannel.append(result.stdout);
        outputChannel.show();
      } else {
        vscode.window.showErrorMessage(`Report failed: ${result.stderr}`);
      }
    })
  );

  // Ask
  disposables.push(
    vscode.commands.registerCommand('tokencunt.ask', async () => {
      const editor = vscode.window.activeTextEditor;
      const selectedText = editor?.selection && !editor.selection.isEmpty
        ? editor.document.getText(editor.selection)
        : '';

      const prompt = await vscode.window.showInputBox({
        prompt: 'Enter your question for TokenCUNT',
        value: selectedText || ''
      });

      if (!prompt) { return; }

      vscode.window.showInformationMessage('Processing request...');
      const result = await runCliCommand(['ask', `"${prompt}"`]);

      if (result.exitCode === 0) {
        const outputChannel = vscode.window.createOutputChannel('TokenCUNT Response');
        outputChannel.append(result.stdout);
        outputChannel.show();
        
        // Refresh status bar after request
        await refreshStatusBar();
      } else {
        vscode.window.showErrorMessage(`Ask failed: ${result.stderr}`);
      }
    })
  );

  // ===== Category B: Quick Actions =====
  
  // New Session
  disposables.push(
    vscode.commands.registerCommand('tokencunt.newSession', async () => {
      const result = await runCliCommand(['session', 'new']);
      
      if (result.exitCode === 0) {
        vscode.window.showInformationMessage('New session created');
        await refreshStatusBar();
      } else {
        vscode.window.showErrorMessage(`Failed to create session: ${result.stderr}`);
      }
    })
  );

  // Set Budget
  disposables.push(
    vscode.commands.registerCommand('tokencunt.setBudget', async () => {
      const config = vscode.workspace.getConfiguration('tokencunt');
      const currentBudget = config.get<number>('budget') || 10000;
      
      const budgetStr = await vscode.window.showInputBox({
        prompt: 'Enter token budget',
        value: currentBudget.toString(),
        validateInput: (value: string) => {
          const num = parseInt(value, 10);
          return (!isNaN(num) && num > 0 && num <= 1000000) 
            ? null 
            : 'Enter a number between 1 and 1,000,000';
        }
      });

      if (!budgetStr) { return; }

      const budget = parseInt(budgetStr, 10);
      await config.update('budget', budget, vscode.ConfigurationTarget.Global);
      
      vscode.window.showInformationMessage(`Budget set to ${budget.toLocaleString()} tokens`);
      await refreshStatusBar();
    })
  );

  // Clear Session
  disposables.push(
    vscode.commands.registerCommand('tokencunt.clearSession', async () => {
      const result = await runCliCommand(['session', 'clear']);
      
      if (result.exitCode === 0) {
        vscode.window.showInformationMessage('Session cleared');
        resetStatusBar();
      } else {
        vscode.window.showErrorMessage(`Failed to clear session: ${result.stderr}`);
      }
    })
  );

  // ===== Category C: Settings =====
  
  // Configure API Key
  disposables.push(
    vscode.commands.registerCommand('tokencunt.configureApiKey', async () => {
      const config = vscode.workspace.getConfiguration('tokencunt');
      const currentKey = config.get<string>('apiKey') || '';
      
      // Show masked version if key exists
      const placeholder = currentKey 
        ? `Current key: ${currentKey.substring(0, 8)}...` 
        : 'Enter your MiniMax API Key';
        
      const apiKey = await vscode.window.showInputBox({
        prompt: placeholder,
        password: true,
        ignoreFocusOut: true
      });

      if (apiKey === undefined) { return; }  // Cancelled
      
      // If empty string provided, clear the key
      if (apiKey === '') {
        await config.update('apiKey', undefined, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage('API Key cleared');
        return;
      }

      await config.update('apiKey', apiKey, vscode.ConfigurationTarget.Global);
      vscode.window.showInformationMessage('API Key configured successfully');
    })
  );

  // Configure Model
  disposables.push(
    vscode.commands.registerCommand('tokencunt.configureModel', async () => {
      const models = ['abab6.5-chat', 'abab6.5s-chat', 'abab5.5-chat'];
      const modelItems: vscode.QuickPickItem[] = models.map(m => ({ label: m }));
      
      const config = vscode.workspace.getConfiguration('tokencunt');
      const currentModel = config.get<string>('model') || 'abab6.5-chat';
      
      const selected = await vscode.window.showQuickPick(modelItems, {
        placeHolder: 'Select model',
      });

      if (!selected) { return; }

      await config.update('model', selected.label, vscode.ConfigurationTarget.Global);
      vscode.window.showInformationMessage(`Model set to ${selected.label}`);
    })
  );

  // View Settings
  disposables.push(
    vscode.commands.registerCommand('tokencunt.viewSettings', async () => {
      const config = vscode.workspace.getConfiguration('tokencunt');
      const settings = {
        apiKey: config.get<string>('apiKey') ? '[configured]' : '[not set]',
        groupId: config.get<string>('groupId') || '[not set]',
        model: config.get<string>('model') || 'abab6.5-chat',
        budget: config.get<number>('budget') || 10000,
        autoShowSetup: config.get<boolean>('autoShowSetup') ?? true,
        cliPath: config.get<string>('cliPath') || '[default]'
      };

      const outputChannel = vscode.window.createOutputChannel('TokenCUNT Settings');
      outputChannel.appendLine('Current TokenCUNT Settings:');
      outputChannel.appendLine(JSON.stringify(settings, null, 2));
      outputChannel.show();
    })
  );

  // Register quick pick command
  disposables.push(
    vscode.commands.registerCommand('tokencunt.showQuickPick', async () => {
      const items: vscode.QuickPickItem[] = [
        { label: '⚡ New Session', description: 'Start a new token tracking session' },
        { label: '📊 Show Report', description: 'View current usage report' },
        { label: '💰 Set Budget', description: 'Configure token budget limit' },
        { label: '🔍 Analyze File', description: 'Analyze selected code' },
        { label: '', description: '❓ AskAsk TokenCUNT a question' },
        { label: '🗑️ Clear Session', description: 'Clear current session' },
        { label: '⚙️ Configure API Key', description: 'Set your MiniMax API key' },
        { label: '🔧 Configure Model', description: 'Select AI model' },
        { label: '📋 View Settings', description: 'Show current settings' }
      ];

      const selected = await vscode.window.showQuickPick(items, {
        placeHolder: 'TokenCUNT Actions',
        matchOnDescription: true
      });

      if (!selected) { return; }

      // Map back to commands
      const commandMap: Record<string, string> = {
        '⚡ New Session': 'tokencunt.newSession',
        '📊 Show Report': 'tokencunt.showReport',
        '💰 Set Budget': 'tokencunt.setBudget',
        '🔍 Analyze File': 'tokencunt.analyzeFile',
        '❓ Ask': 'tokencunt.ask',
        '🗑️ Clear Session': 'tokencunt.clearSession',
        '⚙️ Configure API Key': 'tokencunt.configureApiKey',
        '🔧 Configure Model': 'tokencunt.configureModel',
        '📋 View Settings': 'tokencunt.viewSettings'
      };

      const command = commandMap[selected.label];
      if (command) {
        vscode.commands.executeCommand(command);
      }
    })
  );

  return disposables;
}
