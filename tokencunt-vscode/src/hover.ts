import * as vscode from 'vscode';
import { runCliCommand } from './cli';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Register hover provider for token estimation
 * Shows token count when hovering over selected text
 */
export function registerHoverProvider(): vscode.Disposable[] {
  const disposables: vscode.Disposable[] = [];
  
  const hoverProvider = vscode.languages.registerHoverProvider(
    '*',  // All languages
    {
      provideHover(document: vscode.TextDocument, position: vscode.Position): vscode.Hover | undefined {
        const editor = vscode.window.activeTextEditor;
        
        // Only show hover when there's a selection
        if (!editor || editor.selection.isEmpty) {
          return undefined;
        }
        
        const selection = editor.selection;
        const selectedText = document.getText(selection);
        
        if (!selectedText || selectedText.trim().length === 0) {
          return undefined;
        }
        
        // Show loading hover (will be updated asynchronously)
        const tokenCount = estimateTokens(selectedText);
        
        const content = new vscode.MarkdownString();
        content.appendMarkdown(`**TokenCUNT Token Estimate**\n\n`);
        content.appendMarkdown(`- **Tokens:** ~${tokenCount.toLocaleString()}\n`);
        content.appendMarkdown(`- **Characters:** ${selectedText.length.toLocaleString()}\n\n`);
        content.appendMarkdown(`*[Click to analyze with TokenCUNT]*`);
        
        return new vscode.Hover(content, selection);
      }
    }
  );
  
  // Add command for "Send to TokenCUNT" action
  const sendToTokenCunt = vscode.commands.registerCommand(
    'tokencunt.sendToTokenCunt',
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || editor.selection.isEmpty) {
        vscode.window.showWarningMessage('No text selected');
        return;
      }
      
      const selectedText = editor.document.getText(editor.selection);
      
      // Create temp file and analyze
      const tempFile = path.join(
        require('os').tmpdir(),
        `tokencunt_analysis_${Date.now()}.txt`
      );
      
      try {
        fs.writeFileSync(tempFile, selectedText, 'utf-8');
        
        const result = await runCliCommand(['analyze', '--file', tempFile]);
        
        if (result.exitCode === 0) {
          const outputChannel = vscode.window.createOutputChannel('TokenCUNT Analysis');
          outputChannel.append(result.stdout);
          outputChannel.show();
        } else {
          vscode.window.showErrorMessage(`Analysis failed: ${result.stderr}`);
        }
      } finally {
        // Cleanup temp file
        try {
          fs.unlinkSync(tempFile);
        } catch {
          // Ignore cleanup errors
        }
      }
    }
  );
  
  // Subscribe to disposables
  vscode.workspace.onDidChangeConfiguration(() => {
    // Could reload config here if needed
  });
  
  disposables.push(hoverProvider, sendToTokenCunt);
  
  // Return disposables for cleanup
  return disposables;
}

/**
 * Simple token estimation (rough estimate: ~4 chars per token)
 * For accurate count, use CLI analyze command
 */
function estimateTokens(text: string): number {
  // Rough estimate: 4 characters per token on average
  const charEstimate = Math.ceil(text.length / 4);
  
  // Adjust for whitespace (more efficient)
  const words = text.split(/\s+/).filter(w => w.length > 0).length;
  
  // Use the average of both methods for better estimate
  return Math.round((charEstimate + words) / 2);
}

/**
 * Get token estimate for selected text asynchronously
 * Uses CLI for accurate counting
 */
export async function getTokenEstimate(text: string): Promise<number> {
  const tempFile = path.join(
    require('os').tmpdir(),
    `tokencunt_estimate_${Date.now()}.txt`
  );
  
  try {
    fs.writeFileSync(tempFile, text, 'utf-8');
    
    const result = await runCliCommand(['analyze', '--file', tempFile]);
    
    if (result.exitCode === 0) {
      // Try to parse token count from output
      const match = result.stdout.match(/tokens[:\s]+(\d+)/i);
      if (match) {
        return parseInt(match[1], 10);
      }
    }
    
    // Fall back to estimate
    return estimateTokens(text);
  } finally {
    try {
      fs.unlinkSync(tempFile);
    } catch {
      // Ignore cleanup errors
    }
  }
}
