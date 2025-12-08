/**
 * Auto Refactor AI VS Code Extension
 * 
 * This extension provides integration with the Auto Refactor AI Python analyzer
 * via the Language Server Protocol (LSP).
 */

import * as vscode from 'vscode';
import * as path from 'path';
import {
    LanguageClient,
    LanguageClientOptions,
    Executable
} from 'vscode-languageclient/node';

let client: LanguageClient | undefined;

export function activate(context: vscode.ExtensionContext) {
    console.log('Auto Refactor AI extension is now active');

    // Get configuration
    const config = vscode.workspace.getConfiguration('autoRefactorAi');
    const pythonPath = config.get<string>('pythonPath', 'python');

    // Server options - start the Python LSP server
    const serverExecutable: Executable = {
        command: pythonPath,
        args: ['-m', 'auto_refactor_ai.lsp_server']
    };

    // Client options
    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'python' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.py')
        },
        outputChannelName: 'Auto Refactor AI',
    };

    // Create the language client
    client = new LanguageClient(
        'autoRefactorAi',
        'Auto Refactor AI',
        serverExecutable,
        clientOptions
    );

    // Register commands
    const analyzeCommand = vscode.commands.registerCommand(
        'auto-refactor-ai.analyze',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            vscode.window.showInformationMessage('Analyzing file...');
            // The LSP server handles analysis automatically on save
            await editor.document.save();
        }
    );

    const showExplanationCommand = vscode.commands.registerCommand(
        'auto-refactor-ai.showExplanation',
        async (args: { title: string; why: string; how: string[] }) => {
            if (!args) {
                return;
            }

            const panel = vscode.window.createWebviewPanel(
                'autoRefactorExplanation',
                args.title,
                vscode.ViewColumn.Beside,
                {}
            );

            panel.webview.html = getExplanationHtml(args);
        }
    );

    context.subscriptions.push(analyzeCommand);
    context.subscriptions.push(showExplanationCommand);

    // Start the client
    client.start();

    context.subscriptions.push({
        dispose: () => {
            if (client) {
                client.stop();
            }
        }
    });
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

function getExplanationHtml(args: { title: string; why: string; how: string[] }): string {
    const howSteps = args.how?.map(step => `<li>${step}</li>`).join('\n') || '';

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${args.title}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }
        h1 { color: #0078d4; }
        h2 { color: #666; margin-top: 20px; }
        ul { padding-left: 20px; }
        li { margin: 8px 0; }
    </style>
</head>
<body>
    <h1>${args.title}</h1>
    
    <h2>Why it matters</h2>
    <p>${args.why}</p>
    
    <h2>How to fix</h2>
    <ul>
        ${howSteps}
    </ul>
</body>
</html>`;
}
