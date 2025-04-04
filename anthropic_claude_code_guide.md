
---

# Anthropic Claude Code Guide

## Overview

Claude Code is an agentic coding tool developed by Anthropic, designed to streamline development workflows through natural language commands. It integrates directly with your terminal, understands your codebase, and performs real operations like editing files, resolving merge conflicts, and creating commits.

---

## Table of Contents

1. [Before You Begin](#before-you-begin)
2. [Install and Authenticate](#install-and-authenticate)
3. [Core Features and Workflows](#core-features-and-workflows)
4. [Security and Privacy by Design](#security-and-privacy-by-design)
5. [Using Claude Code](#using-claude-code)
6. [Manage Permissions and Security](#manage-permissions-and-security)
7. [Configure Claude Code](#configure-claude-code)
8. [Optimize Your Terminal Setup](#optimize-your-terminal-setup)
9. [Manage Costs Effectively](#manage-costs-effectively)
10. [Model Configuration](#model-configuration)
11. [Use with Third-Party APIs](#use-with-third-party-apis)
12. [Development Container Reference Implementation](#development-container-reference-implementation)
13. [License and Data Usage](#license-and-data-usage)

---

## Before You Begin

### System Requirements

- **Operating Systems**: macOS 10.15+, Ubuntu 20.04+/Debian 10+, or Windows via WSL
- **Hardware**: Minimum 4GB RAM
- **Software**:
  - Node.js 18+
  - git 2.23+ (optional)
  - GitHub or GitLab CLI for PR workflows (optional)
  - ripgrep (`rg`) for enhanced file search (optional)
- **Network**: Internet connection required for authentication and AI processing
- **Location**: Available only in supported countries

### Troubleshooting WSL Installation

Claude Code requires WSL for Windows. Common issues include:

- **OS/platform detection issues**: Run `npm config set os linux` before installation.
- **Node not found errors**: Ensure Node.js is installed via your Linux distribution’s package manager or `nvm`.

---

## Install and Authenticate

### Installation Steps

1. **Install Claude Code**  
   Run in your terminal:  
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
   **Do NOT use `sudo npm install -g`** as it can lead to permission issues.

2. **Navigate to Your Project**  
   ```bash
   cd your-project-directory
   ```

3. **Start Claude Code**  
   ```bash
   claude
   ```

4. **Complete Authentication**  
   Follow the one-time OAuth process with your Console account. Active billing is required at [console.anthropic.com](https://console.anthropic.com).

---

## Core Features and Workflows

Claude Code operates directly in your terminal, understanding your project context and taking real actions. Key capabilities include:

- **Editing files and fixing bugs** across your codebase
- **Answering questions** about your code’s architecture and logic
- **Executing and fixing tests**, linting, and other commands
- **Searching through git history**, resolving merge conflicts, and creating commits/PRs

---

## Security and Privacy by Design

Claude Code ensures your code’s security through:

- **Direct API connection**: Queries go straight to Anthropic’s API without intermediate servers.
- **Context awareness**: Maintains awareness of your entire project structure.
- **Actionable operations**: Performs real operations like editing files and creating commits.

---

## Using Claude Code

### Common Tasks

#### Understand Unfamiliar Code
```bash
claude
> what does the payment processing system do?
> find where user permissions are checked
> explain how the caching layer works
```

#### Automate Git Operations
```bash
claude commit
claude "create a pr"
claude "rebase on main and resolve merge conflicts"
```

#### Edit Code Intelligently
```bash
claude "add input validation to the signup form"
claude "refactor the logger to use the new API"
claude "fix the race condition in the worker queue"
```

#### Test and Debug Code
```bash
claude "run tests for the auth module and fix failures"
claude "find and fix security vulnerabilities"
claude "explain why this test is failing"
```

---

## Manage Permissions and Security

Claude Code uses a tiered permission system:

| Tool Type         | Example                        | Approval Required | "Yes, Don’t Ask Again" Behavior |
|--------------------|--------------------------------|-------------------|----------------------------------|
| Read-only         | File reads, LS, Grep          | No                | N/A                              |
| Bash Commands     | Shell execution               | Yes               | Permanently per project directory and command |
| File Modification | Edit/write files              | Yes               | Until session end                |

---

## Configure Claude Code

### Configuration Options

#### Global Configuration
Manage global settings with:
```bash
claude config set -g <key> <value>
```

| Key                  | Value                       | Description                              |
|----------------------|-----------------------------|------------------------------------------|
| `autoUpdaterStatus`  | `disabled` or `enabled`    | Enable or disable the auto-updater      |
| `theme`              | `dark`, `light`, etc.      | Color theme                              |
| `verbose`            | `true` or `false`          | Show full bash and command outputs       |

#### Project Configuration
Manage project-specific settings with:
```bash
claude config set <key> <value>
```

| Key              | Value                  | Description                              |
|------------------|------------------------|------------------------------------------|
| `allowedTools`   | Array of tools         | Tools that can run without manual approval |
| `ignorePatterns` | Array of glob strings | Files/directories ignored by tools      |

---

## Optimize Your Terminal Setup

### Themes and Appearance
Match Claude Code’s theme to your terminal via `/config`.

### Line Breaks
- **Quick escape**: Type `\` followed by Enter.
- **Keyboard shortcut**: Press Option+Enter (Meta+Enter).

### Notification Setup
Enable sound alerts for task completion:
```bash
claude config set --global preferredNotifChannel terminal_bell
```

---

## Manage Costs Effectively

### Track Costs
- Use `/cost` to see current session usage.
- Check historical usage in the Anthropic Console.

### Reduce Token Usage
- Compact conversations with `/compact`.
- Write specific queries to avoid unnecessary scanning.
- Clear history between tasks with `/clear`.

---

## Model Configuration

By default, Claude Code uses `claude-3-7-sonnet-20250219`. Override this using environment variables:
```bash
ANTHROPIC_MODEL='claude-3-7-sonnet-20250219'
```

---

## Use with Third-Party APIs

### Connect to Amazon Bedrock
```bash
CLAUDE_CODE_USE_BEDROCK=1
ANTHROPIC_BEDROCK_BASE_URL='https://your-proxy-url'
```

### Connect to Google Vertex AI
```bash
CLAUDE_CODE_USE_VERTEX=1
CLOUD_ML_REGION=us-east5
ANTHROPIC_VERTEX_PROJECT_ID=your-project-id
```

---

## Development Container Reference Implementation

Claude Code provides a preconfigured development container setup for secure environments.

### Key Features
- **Production-ready Node.js**: Built on Node.js 20.
- **Security by design**: Custom firewall restricting network access.
- **Developer-friendly tools**: Includes git, ZSH, fzf, and more.

---

## License and Data Usage

Claude Code is provided as a Beta research preview under Anthropic’s Commercial Terms of Service.

### Privacy Safeguards
- Limited retention periods for sensitive information.
- Restricted access to user session data.
- Clear policies against using feedback for model training.

For full details, review Anthropic’s [Commercial Terms of Service](https://console.anthropic.com/legal) and [Privacy Policy](https://console.anthropic.com/privacy).

---

Was this page helpful?  
[Yes](#) | [No](#)