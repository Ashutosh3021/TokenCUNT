import * as vscode from 'vscode';

/**
 * Show the setup webview for first-time configuration
 */
let setupPanel: vscode.WebviewPanel | undefined;

export async function showSetupWebview(): Promise<void> {
  // If panel already exists, reveal it
  if (setupPanel) {
    setupPanel.reveal(vscode.ViewColumn.One);
    return;
  }

  // Create new panel
  setupPanel = vscode.window.createWebviewPanel(
    'tokencunt-setup',
    'TokenCUNT Setup',
    vscode.ViewColumn.One,
    {
      enableScripts: true,
      retainContextWhenHidden: true,
      localResourceRoots: []
    }
  );

  // Set HTML content
  setupPanel.webview.html = getSetupHtml();

  // Handle messages from webview
  setupPanel.webview.onDidReceiveMessage(async (message) => {
    switch (message.command) {
      case 'save':
        await saveConfiguration(message.data);
        setupPanel?.dispose();
        setupPanel = undefined;
        vscode.window.showInformationMessage('TokenCUNT configured successfully!');
        break;
      
      case 'cancel':
        setupPanel?.dispose();
        setupPanel = undefined;
        break;
        
      case 'validateKey':
        // Simple validation - check key format
        const isValid = validateApiKey(message.data.apiKey);
        setupPanel?.webview.postMessage({ 
          command: 'validationResult', 
          valid: isValid,
          error: isValid ? '' : 'Invalid API key format'
        });
        break;
    }
  });

  // Handle panel close
  setupPanel.onDidDispose(() => {
    setupPanel = undefined;
  });
}

/**
 * Save configuration from setup webview
 */
async function saveConfiguration(data: {
  apiKey: string;
  groupId: string;
  model: string;
  budget: number;
}): Promise<void> {
  const config = vscode.workspace.getConfiguration('tokencunt');
  
  if (data.apiKey) {
    await config.update('apiKey', data.apiKey, vscode.ConfigurationTarget.Global);
  }
  
  if (data.groupId) {
    await config.update('groupId', data.groupId, vscode.ConfigurationTarget.Global);
  }
  
  if (data.model) {
    await config.update('model', data.model, vscode.ConfigurationTarget.Global);
  }
  
  if (data.budget > 0) {
    await config.update('budget', data.budget, vscode.ConfigurationTarget.Global);
  }
  
  // Mark setup as complete
  await config.update('autoShowSetup', false, vscode.ConfigurationTarget.Global);
}

/**
 * Validate API key format (MiniMax keys start with specific prefix)
 */
function validateApiKey(key: string): boolean {
  if (!key || key.length < 10) { return false; }
  // MiniMax API keys are typically longer alphanumeric strings
  return /^[a-zA-Z0-9_-]{10,}$/.test(key);
}

/**
 * Get HTML content for setup webview
 */
function getSetupHtml(): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TokenCUNT Setup</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      padding: 24px;
      background-color: var(--vscode-editor-background, #1e1e1e);
      color: var(--vscode-editor-foreground, #d4d4d4);
    }
    
    .container {
      max-width: 500px;
      margin: 0 auto;
    }
    
    h1 {
      font-size: 24px;
      margin-bottom: 8px;
      color: var(--vscode-editor-foreground, #d4d4d4);
    }
    
    .subtitle {
      color: var(--vscode-editor-foreground, #858585);
      margin-bottom: 24px;
    }
    
    .form-group {
      margin-bottom: 20px;
    }
    
    label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
    }
    
    input, select {
      width: 100%;
      padding: 8px 12px;
      border: 1px solid var(--vscode-input-border, #3c3c3c);
      border-radius: 4px;
      background-color: var(--vscode-input-background, #252526);
      color: var(--vscode-editor-foreground, #d4d4d4);
      font-size: 14px;
    }
    
    input:focus, select:focus {
      outline: 2px solid var(--vscode-focusBorder, #007acc);
      border-color: transparent;
    }
    
    .hint {
      font-size: 12px;
      color: var(--vscode-editor-foreground, #858585);
      margin-top: 4px;
    }
    
    .error {
      color: #f48771;
      font-size: 12px;
      margin-top: 4px;
      display: none;
    }
    
    .error.visible {
      display: block;
    }
    
    .actions {
      display: flex;
      gap: 12px;
      margin-top: 28px;
    }
    
    button {
      padding: 8px 16px;
      border-radius: 4px;
      font-size: 14px;
      cursor: pointer;
      border: none;
    }
    
    .btn-primary {
      background-color: var(--vscode-button-background, #0e639c);
      color: var(--vscode-button-foreground, #ffffff);
    }
    
    .btn-primary:hover {
      background-color: var(--vscode-button-hoverBackground, #1177bb);
    }
    
    .btn-secondary {
      background-color: transparent;
      color: var(--vscode-button-foreground, #d4d4d4);
      border: 1px solid var(--vscode-button-secondaryBackground, #3c3c3c);
    }
    
    .btn-secondary:hover {
      background-color: var(--vscode-button-secondaryHoverBackground, #2d2d2d);
    }
    
    .spinner {
      display: none;
      width: 16px;
      height: 16px;
      border: 2px solid #ffffff;
      border-top-color: transparent;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    .loading .btn-text {
      display: none;
    }
    
    .loading .spinner {
      display: inline-block;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Welcome to TokenCUNT</h1>
    <p class="subtitle">Configure your settings to get started</p>
    
    <form id="setupForm">
      <div class="form-group">
        <label for="apiKey">API Key *</label>
        <input type="password" id="apiKey" required placeholder="Enter your MiniMax API key">
        <p class="hint">Get your API key from MiniMax dashboard</p>
        <p class="error" id="apiKeyError"></p>
      </div>
      
      <div class="form-group">
        <label for="groupId">Group ID</label>
        <input type="text" id="groupId" placeholder="Optional: Enter your Group ID">
        <p class="hint">Required for some MiniMax API calls</p>
      </div>
      
      <div class="form-group">
        <label for="model">Model</label>
        <select id="model">
          <option value="abab6.5-chat" selected>abab6.5-chat (Recommended)</option>
          <option value="abab6.5s-chat">abab6.5s-chat</option>
          <option value="abab5.5-chat">abab5.5-chat</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="budget">Token Budget</label>
        <input type="number" id="budget" value="10000" min="100" max="1000000" step="1000">
        <p class="hint">Session budget limit (default: 10,000)</p>
      </div>
      
      <div class="actions">
        <button type="submit" class="btn-primary" id="saveBtn">
          <span class="btn-text">Save & Continue</span>
          <span class="spinner"></span>
        </button>
        <button type="button" class="btn-secondary" id="cancelBtn">Cancel</button>
      </div>
    </form>
  </div>
  
  <script>
    const vscode = acquireVsCodeApi();
    
    const form = document.getElementById('setupForm');
    const saveBtn = document.getElementById('saveBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const apiKeyInput = document.getElementById('apiKey');
    const apiKeyError = document.getElementById('apiKeyError');
    
    // Validate on blur
    apiKeyInput.addEventListener('blur', () => {
      if (apiKeyInput.value) {
        vscode.postMessage({
          command: 'validateKey',
          data: { apiKey: apiKeyInput.value }
        });
      }
    });
    
    // Handle validation results
    window.addEventListener('message', (event) => {
      const message = event.data;
      if (message.command === 'validationResult') {
        if (message.valid) {
          apiKeyError.classList.remove('visible');
        } else {
          apiKeyError.textContent = message.error;
          apiKeyError.classList.add('visible');
        }
      }
    });
    
    // Save configuration
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      
      saveBtn.classList.add('loading');
      saveBtn.disabled = true;
      
      const data = {
        apiKey: apiKeyInput.value,
        groupId: document.getElementById('groupId').value,
        model: document.getElementById('model').value,
        budget: parseInt(document.getElementById('budget').value, 10) || 10000
      };
      
      vscode.postMessage({
        command: 'save',
        data: data
      });
    });
    
    // Cancel
    cancelBtn.addEventListener('click', () => {
      vscode.postMessage({ command: 'cancel' });
    });
  </script>
</body>
</html>`;
}

/**
 * Check if setup has been completed
 */
export async function isSetupComplete(): Promise<boolean> {
  const config = vscode.workspace.getConfiguration('tokencunt');
  const apiKey = config.get<string>('apiKey');
  return !!apiKey;
}
