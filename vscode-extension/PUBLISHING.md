# Publishing Guide for Auto Refactor AI VS Code Extension

## Quick Start

The extension is already packaged as:
```
vscode-extension/auto-refactor-ai-0.11.0.vsix
```

## Local Installation

Already tested and installed:
```bash
code --install-extension auto-refactor-ai-0.11.0.vsix
```

---

## Publishing to VS Code Marketplace

### Step 1: Create Publisher Account

1. Go to https://marketplace.visualstudio.com/manage
2. Sign in with Microsoft account
3. Create a publisher (e.g., "auto-refactor-ai")

### Step 2: Get Personal Access Token (PAT)

1. Go to https://dev.azure.com
2. User Settings → Personal Access Tokens
3. Create new token with:
   - Organization: All accessible organizations
   - Scopes: Marketplace → Manage

### Step 3: Update package.json

```json
{
  "publisher": "your-publisher-name",
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/auto-refactor-ai"
  }
}
```

### Step 4: Login and Publish

```bash
cd vscode-extension

# Login with PAT
vsce login your-publisher-name

# Publish (will ask for PAT)
vsce publish
```

### Step 5: Verify

Visit: https://marketplace.visualstudio.com/items?itemName=your-publisher-name.auto-refactor-ai

---

## Alternative: Publish on OpenVSX (for non-Microsoft editors)

```bash
npm install -g ovsx
ovsx publish auto-refactor-ai-0.11.0.vsix -p YOUR_OPENVSX_TOKEN
```

---

## Updating the Extension

```bash
# Bump version
npm version patch  # or minor, major

# Repackage and publish
vsce package
vsce publish
```

---

## Files Required for Publishing

| File | Purpose |
|------|---------|
| `package.json` | Extension manifest |
| `README.md` | Marketplace description |
| `CHANGELOG.md` | Version history |
| `LICENSE` | License file |
| `.vscodeignore` | Exclude dev files |
| `out/extension.js` | Compiled code |
