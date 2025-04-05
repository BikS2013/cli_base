```markdown
# Claude Code Tutorials

Practical examples and patterns for effectively using Claude Code in your development workflow.

This guide provides step-by-step tutorials for common workflows with Claude Code. Each tutorial includes clear instructions, example commands, and best practices to help you get the most from Claude Code.

---

## Table of Contents

1. [Understand New Codebases](#understand-new-codebases)  
2. [Fix Bugs Efficiently](#fix-bugs-efficiently)  
3. [Refactor Code](#refactor-code)  
4. [Work with Tests](#work-with-tests)  
5. [Create Pull Requests](#create-pull-requests)  
6. [Handle Documentation](#handle-documentation)  
7. [Work with Images](#work-with-images)  
8. [Use Extended Thinking](#use-extended-thinking)  
9. [Set Up Project Memory](#set-up-project-memory)  
10. [Set Up Model Context Protocol (MCP)](#set-up-model-context-protocol-mcp)  
11. [Use Claude as a Unix-Style Utility](#use-claude-as-a-unix-style-utility)  
12. [Create Custom Slash Commands](#create-custom-slash-commands)  
13. [Run Parallel Claude Code Sessions with Git Worktrees](#run-parallel-claude-code-sessions-with-git-worktrees)  

---

## Understand New Codebases

### Get a Quick Codebase Overview

**When to use:** You’ve just joined a new project and need to understand its structure quickly.

1. Navigate to the project root directory:
   ```bash
   cd /path/to/project
   ```

2. Start Claude Code:
   ```bash
   claude
   ```

3. Ask for a high-level overview:
   ```plaintext
   > give me an overview of this codebase
   ```

4. Dive deeper into specific components:
   ```plaintext
   > explain the main architecture patterns used here  
   > what are the key data models?  
   > how is authentication handled?  
   ```

**Tips:**
- Start with broad questions, then narrow down to specific areas.
- Ask about coding conventions and patterns used in the project.
- Request a glossary of project-specific terms.

---

### Find Relevant Code

**When to use:** You need to locate code related to a specific feature or functionality.

1. Ask Claude to find relevant files:
   ```plaintext
   > find the files that handle user authentication
   ```

2. Get context on how components interact:
   ```plaintext
   > how do these authentication files work together?
   ```

3. Understand the execution flow:
   ```plaintext
   > trace the login process from front-end to database
   ```

**Tips:**
- Be specific about what you’re looking for.
- Use domain language from the project.

---

## Fix Bugs Efficiently

### Diagnose Error Messages

**When to use:** You’ve encountered an error message and need to find and fix its source.

1. Share the error with Claude:
   ```plaintext
   > I'm seeing an error when I run npm test
   ```

2. Ask for fix recommendations:
   ```plaintext
   > suggest a few ways to fix the @ts-ignore in user.ts
   ```

3. Apply the fix:
   ```plaintext
   > update user.ts to add the null check you suggested
   ```

**Tips:**
- Tell Claude the command to reproduce the issue and get a stack trace.
- Mention any steps to reproduce the error.
- Let Claude know if the error is intermittent or consistent.

---

## Refactor Code

### Modernize Legacy Code

**When to use:** You need to update old code to use modern patterns and practices.

1. Identify legacy code for refactoring:
   ```plaintext
   > find deprecated API usage in our codebase
   ```

2. Get refactoring recommendations:
   ```plaintext
   > suggest how to refactor utils.js to use modern JavaScript features
   ```

3. Apply the changes safely:
   ```plaintext
   > refactor utils.js to use ES2024 features while maintaining the same behavior
   ```

4. Verify the refactoring:
   ```plaintext
   > run tests for the refactored code
   ```

**Tips:**
- Ask Claude to explain the benefits of the modern approach.
- Request that changes maintain backward compatibility when needed.
- Do refactoring in small, testable increments.

---

## Work with Tests

### Add Test Coverage

**When to use:** You need to add tests for uncovered code.

1. Identify untested code:
   ```plaintext
   > find functions in NotificationsService.swift that are not covered by tests
   ```

2. Generate test scaffolding:
   ```plaintext
   > add tests for the notification service
   ```

3. Add meaningful test cases:
   ```plaintext
   > add test cases for edge conditions in the notification service
   ```

4. Run and verify tests:
   ```plaintext
   > run the new tests and fix any failures
   ```

**Tips:**
- Ask for tests that cover edge cases and error conditions.
- Request both unit and integration tests when appropriate.
- Have Claude explain the testing strategy.

---

## Create Pull Requests

### Generate Comprehensive PRs

**When to use:** You need to create a well-documented pull request for your changes.

1. Summarize your changes:
   ```plaintext
   > summarize the changes I've made to the authentication module
   ```

2. Generate a PR with Claude:
   ```plaintext
   > create a pr
   ```

3. Review and refine:
   ```plaintext
   > enhance the PR description with more context about the security improvements
   ```

4. Add testing details:
   ```plaintext
   > add information about how these changes were tested
   ```

**Tips:**
- Ask Claude directly to make a PR for you.
- Review Claude’s generated PR before submitting.
- Ask Claude to highlight potential risks or considerations.

---

## Handle Documentation

### Generate Code Documentation

**When to use:** You need to add or update documentation for your code.

1. Identify undocumented code:
   ```plaintext
   > find functions without proper JSDoc comments in the auth module
   ```

2. Generate documentation:
   ```plaintext
   > add JSDoc comments to the undocumented functions in auth.js
   ```

3. Review and enhance:
   ```plaintext
   > improve the generated documentation with more context and examples
   ```

4. Verify documentation:
   ```plaintext
   > check if the documentation follows our project standards
   ```

**Tips:**
- Specify the documentation style you want (JSDoc, docstrings, etc.).
- Ask for examples in the documentation.
- Request documentation for public APIs, interfaces, and complex logic.

---

**[Continue to next sections...]**
```

Let me know if you'd like me to continue formatting the remaining sections!

```markdown
---

## Work with Images

### Analyze Images and Screenshots

**When to use:** You need to work with images in your codebase or get Claude’s help analyzing image content.

1. Add an image to the conversation:  
   You can use any of these methods:
   - Drag and drop an image into the Claude Code window.
   - Copy an image and paste it into the CLI with `ctrl+v`.
   - Provide an image path:
     ```bash
     claude "Analyze this image: /path/to/your/image.png"
     ```

2. Ask Claude to analyze the image:
   ```plaintext
   > What does this image show?  
   > Describe the UI elements in this screenshot.  
   > Are there any problematic elements in this diagram?  
   ```

3. Use images for context:
   ```plaintext
   > Here's a screenshot of the error. What's causing it?  
   > This is our current database schema. How should we modify it for the new feature?  
   ```

4. Get code suggestions from visual content:
   ```plaintext
   > Generate CSS to match this design mockup.  
   > What HTML structure would recreate this component?  
   ```

**Tips:**
- Use images when text descriptions would be unclear or cumbersome.
- Include screenshots of errors, UI designs, or diagrams for better context.
- You can work with multiple images in a conversation.
- Image analysis works with diagrams, screenshots, mockups, and more.

---

## Use Extended Thinking

### Leverage Claude’s Extended Thinking for Complex Tasks

**When to use:** When working on complex architectural decisions, challenging bugs, or planning multi-step implementations that require deep reasoning.

1. Provide context and ask Claude to think:
   ```plaintext
   > I need to implement a new authentication system using OAuth2 for our API. Think deeply about the best approach for implementing this in our codebase.
   ```

   Claude will gather relevant information from your codebase and use extended thinking, which will be visible in the interface.

2. Refine the thinking with follow-up prompts:
   ```plaintext
   > think about potential security vulnerabilities in this approach  
   > think harder about edge cases we should handle  
   ```

**Tips to Get the Most Value Out of Extended Thinking:**
- Extended thinking is most valuable for complex tasks such as:
  - Planning complex architectural changes.
  - Debugging intricate issues.
  - Creating implementation plans for new features.
  - Understanding complex codebases.
  - Evaluating tradeoffs between different approaches.
- The way you prompt for thinking results in varying levels of thinking depth:
  - `"think"` triggers basic extended thinking.
  - Intensifying phrases such as `"think more"`, `"think a lot"`, `"think harder"`, or `"think longer"` trigger deeper thinking.
- Claude will display its thinking process as *italic gray text* above the response.

---

## Set Up Project Memory

### Create an Effective `CLAUDE.md` File

**When to use:** You want to set up a `CLAUDE.md` file to store important project information, conventions, and frequently used commands.

1. Bootstrap a `CLAUDE.md` for your codebase:
   ```plaintext
   > /init
   ```

**Tips:**
- Include frequently used commands (build, test, lint) to avoid repeated searches.
- Document code style preferences and naming conventions.
- Add important architectural patterns specific to your project.

**Where You Can Add `CLAUDE.md` Files:**
- The folder you run Claude in: Automatically added to conversations you start in that folder.
- Child directories: Claude pulls these in on demand.
- `~/.claude/CLAUDE.md`: User-specific preferences that you don’t want to check into source control.

---

## Set Up Model Context Protocol (MCP)

Model Context Protocol (MCP) is an open protocol that enables LLMs to access external tools and data sources. For more details, see the [MCP documentation](#).

**Use third-party MCP servers at your own risk.** Make sure you trust the MCP servers, and be especially careful when using MCP servers that talk to the internet, as these can expose you to prompt injection risk.

### Configure MCP Servers

**When to use:** You want to enhance Claude’s capabilities by connecting it to specialized tools and external servers using the Model Context Protocol.

1. Add an MCP Stdio Server:
   ```bash
   # Basic syntax
   claude mcp add <name> <command> [args...]

   # Example: Adding a local server
   claude mcp add my-server -e API_KEY=123 -- /path/to/server arg1 arg2
   ```

2. Add an MCP SSE Server:
   ```bash
   # Basic syntax
   claude mcp add --transport sse <name> <url>

   # Example: Adding an SSE server
   claude mcp add --transport sse sse-server https://example.com/sse-endpoint
   ```

3. Manage your MCP servers:
   ```bash
   # List all configured servers
   claude mcp list

   # Get details for a specific server
   claude mcp get my-server

   # Remove a server
   claude mcp remove my-server
   ```

**Tips:**
- Use the `-s` or `--scope` flag to specify where the configuration is stored:
  - `local` (default): Available only to you in the current project (was called `project` in older versions).
  - `project`: Shared with everyone in the project via `.mcp.json` file.
  - `user`: Available to you across all projects (was called `global` in older versions).
- Set environment variables with `-e` or `--env` flags (e.g., `-e KEY=value`).
- Configure MCP server startup timeout using the `MCP_TIMEOUT` environment variable (e.g., `MCP_TIMEOUT=10000 claude` sets a 10-second timeout).
- Check MCP server status any time using the `/mcp` command within Claude Code.
- MCP follows a client-server architecture where Claude Code (the client) can connect to multiple specialized servers.

---

## Use Claude as a Unix-Style Utility

### Add Claude to Your Verification Process

**When to use:** You want to use Claude Code as a linter or code reviewer.

1. Add Claude to your build script:
   ```json
   // package.json
   {
       ...
       "scripts": {
           ...
           "lint:claude": "claude -p 'you are a linter. please look at the changes vs. main and report any issues related to typos. report the filename and line number on one line, and a description of the issue on the second line. do not return any other text.'"
       }
   }
   ```

---

## Create Custom Slash Commands

### Create Project-Specific Commands

**When to use:** You want to create reusable slash commands for your project that all team members can use.

1. Create a commands directory in your project:
   ```bash
   mkdir -p .claude/commands
   ```

2. Create a Markdown file for each command:
   ```bash
   echo "Analyze the performance of this code and suggest three specific optimizations:" > .claude/commands/optimize.md
   ```

3. Use your custom command in Claude Code:
   ```plaintext
   claude
   > /project:optimize
   ```

**Tips:**
- Command names are derived from the filename (e.g., `optimize.md` becomes `/project:optimize`).
- You can organize commands in subdirectories (e.g., `.claude/commands/frontend/component.md` becomes `/project:frontend:component`).
- Project commands are available to everyone who clones the repository.
- The Markdown file content becomes the prompt sent to Claude when the command is invoked.

---

## Run Parallel Claude Code Sessions with Git Worktrees

### Use Worktrees for Isolated Coding Environments

**When to use:** You need to work on multiple tasks simultaneously with complete code isolation between Claude Code instances.

1. Understand Git worktrees:  
   Git worktrees allow you to check out multiple branches from the same repository into separate directories. Each worktree has its own working directory with isolated files, while sharing the same Git history. Learn more in the [official Git worktree documentation](https://git-scm.com/docs/git-worktree).

2. Create a new worktree:
   ```bash
   # Create a new worktree with a new branch
   git worktree add ../project-feature-a feature-a

   # Or create a worktree with an existing branch
   git worktree add ../project-bugfix bugfix-123
   ```

3. Run Claude Code in each worktree:
   ```bash
   # Navigate to your worktree
   cd ../project-feature-a

   # Run Claude Code in this isolated environment
   claude
   ```

   In another terminal:
   ```bash
   cd ../project-bugfix
   claude
   ```

4. Manage your worktrees:
   ```bash
   # List all worktrees
   git worktree list

   # Remove a worktree when done
   git worktree remove ../project-feature-a
   ```

**Tips:**
- Each worktree has its own independent file state, making it perfect for parallel Claude Code sessions.
- Changes made in one worktree won’t affect others, preventing Claude instances from interfering with each other.
- All worktrees share the same Git history and remote connections.
- Use descriptive directory names to easily identify which task each worktree is for.

---

**Conversion Complete.** Let me know if you need further adjustments or additional sections formatted!
```