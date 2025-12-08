"use strict";
/**
 * Auto Refactor AI VS Code Extension
 *
 * This extension provides integration with the Auto Refactor AI Python analyzer
 * via the Language Server Protocol (LSP).
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const node_1 = require("vscode-languageclient/node");
let client;
function activate(context) {
    console.log('Auto Refactor AI extension is now active');
    // Get configuration
    const config = vscode.workspace.getConfiguration('autoRefactorAi');
    const pythonPath = config.get('pythonPath', 'python');
    // Server options - start the Python LSP server
    const serverExecutable = {
        command: pythonPath,
        args: ['-m', 'auto_refactor_ai.lsp_server']
    };
    // Client options
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'python' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.py')
        },
        outputChannelName: 'Auto Refactor AI',
    };
    // Create the language client
    client = new node_1.LanguageClient('autoRefactorAi', 'Auto Refactor AI', serverExecutable, clientOptions);
    // Register commands
    const analyzeCommand = vscode.commands.registerCommand('auto-refactor-ai.analyze', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }
        vscode.window.showInformationMessage('Analyzing file...');
        // The LSP server handles analysis automatically on save
        await editor.document.save();
    });
    const showExplanationCommand = vscode.commands.registerCommand('auto-refactor-ai.showExplanation', async (args) => {
        if (!args) {
            return;
        }
        const panel = vscode.window.createWebviewPanel('autoRefactorExplanation', args.title, vscode.ViewColumn.Beside, {});
        panel.webview.html = getExplanationHtml(args);
    });
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
function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
function getExplanationHtml(args) {
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
//# sourceMappingURL=extension.js.map