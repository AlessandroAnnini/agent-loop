# Agent Loop

> **An AI Agent with optional Human-in-the-Loop Safety, Model Context Protocol (MCP) integration, and beautiful, themeable CLI output**

---

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![uv](https://img.shields.io/badge/uv-Package_Manager-7c4dff)
![Anthropic](https://img.shields.io/badge/Anthropic-API-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-API-green?logo=openai)
![MCP](https://img.shields.io/badge/Tool-MCP-4B8BBE?logo=protocols)
**![Version](https://img.shields.io/badge/version-2.2.0-blue)**

## Tools

![Bash](https://img.shields.io/badge/Tool-Bash-black?logo=gnu-bash)
![Python](https://img.shields.io/badge/Tool-Python-3776AB?logo=python)
![Node.js](https://img.shields.io/badge/Tool-Node.js-339933?logo=node.js)
![SymPy](https://img.shields.io/badge/Tool-SymPy-3B5526?logo=python)
![Filesystem](https://img.shields.io/badge/Tool-Filesystem-4B275F)
![HTTP](https://img.shields.io/badge/Tool-HTTP-0099E5?logo=http)
![Curl](https://img.shields.io/badge/Tool-Curl-073551?logo=curl)
![Git](https://img.shields.io/badge/Tool-Git-F05032?logo=git)
![Docker](https://img.shields.io/badge/Tool-Docker-2496ED?logo=docker)
![Project Inspector](https://img.shields.io/badge/Tool-Project_Inspector-lightgrey)
![Kubectl](https://img.shields.io/badge/Tool-Kubectl-326CE5?logo=kubernetes)
![AWS CLI](https://img.shields.io/badge/Tool-AWS_CLI-232F3E?logo=amazon-aws)
![Jira](https://img.shields.io/badge/Tool-Jira-0052CC?logo=jira)
![Confluence](https://img.shields.io/badge/Tool-Confluence-172B4D?logo=confluence)

---

## Requirements

- **Python**: >= 3.12
- **Core Python dependencies:**
  - anthropic >= 0.51.0
  - halo >= 0.0.31
  - mcp[cli] >= 1.9.2
  - openai >= 1.79.0
  - python-dotenv >= 1.1.0
  - requests >= 2.32.3
  - sympy >= 1.14.0
- **Recommended for installation:**
  - [uv](https://astral.sh/uv) (for fast dependency installation)
- **Optional/for full tool support:**
  - Node.js (for some MCP server integrations, e.g., Brave Search, Obsidian)
  - Docker, Git, AWS CLI, kubectl, etc. (for full tool support)
- **Platform:**
  - Linux, macOS, or Windows Subsystem for Linux (WSL)
- **API Keys (for full functionality):**
  - Anthropic API key (for Claude models)
  - OpenAI API key (for GPT models)
  - (Optional) Jira and Confluence API keys for those integrations

## Overview

**Agent Loop** is a command-line AI assistant. It leverages Anthropic's Claude or OpenAI's GPT models and a suite of powerful tools to automate, inspect, and manage your development environment—while keeping you in control with optional human confirmation for every action.

- **Human-in-the-Loop:** Add `--safe` to require confirmation before any tool runs.
- **Functional Programming:** Clean, composable, and testable code.
- **DevOps Ready:** Integrates with Bash, Python, Docker, Git, Kubernetes, AWS, and more.
- **Multi-Provider:** Supports both Anthropic Claude and OpenAI GPT models.
- **MCP Integration:** Dynamically loads and uses tools/services from any MCP-compatible server (see below).

---

## Code Structure

- `main.py` — Main event loop and orchestration
- `cli_input.py` — Terminal input handling (CTRL+C, CTRL+Q, backspace, etc.)
- `signals.py` — Signal handling (SIGINT for interruption)
- `constants.py` — User-facing strings and help messages
- `exceptions.py` — Custom exceptions for clean exit and error handling

All components are designed for modularity, minimalism, and functional programming style.

---

## Graceful Exit and Signal Handling

- **CTRL+C**: Interrupts the current operation and returns to the prompt (does not exit).
- **CTRL+Q** or typing `exit`/`quit` at the prompt: Exits the application cleanly, with no traceback or error.
- Only SIGINT (CTRL+C) is handled as a signal for async safety; quit is handled at the prompt for robust, async-safe shutdown.

---

## Async-Aware LLM Support

Agent Loop automatically supports both synchronous and asynchronous LLM functions, ensuring optimal performance and compatibility. The main event loop will call your LLM function in the most efficient way, whether it is sync or async.

---

## Features

- Conversational AI agent powered by Anthropic Claude or OpenAI GPT
- **Configurable AI provider and temperature** via environment variables
- Tool execution with optional human confirmation (`--safe` mode)
- Debug mode for transparency (`--debug`)
- **Custom tools support** with automatic discovery and display
- **Visual tool differentiation** with distinct icons for built-in, MCP, and custom tools
- Modular, extensible tool system
- Functional programming style throughout
- **Enhanced error handling** with detailed diagnostic information
- **Flexible configuration** with local `.env` file priority
- **MCP (Model Context Protocol) integration for external tool/service discovery and use**

---

## MCP (Model Context Protocol) Integration

**New in v2.0!**

Agent Loop can now connect to any number of MCP-compatible servers, dynamically discovering and using their services as tools. This means you can:

- Add new capabilities (search, knowledge, automation, etc.) by simply running or configuring an MCP server.
- Use tools from remote or local MCP servers as if they were built-in.
- Aggregate services from multiple sources (e.g., Brave Search, Obsidian, custom servers) in one agent.

> **ℹ️ The MCP server configuration format is identical to that used by [Cursor AI IDE](https://docs.cursor.com/context/model-context-protocol#configuring-mcp-servers).**
> See the [Cursor MCP documentation](https://docs.cursor.com/context/model-context-protocol#configuring-mcp-servers) for more details and advanced options.

### How it works

- On startup, Agent Loop reads your MCP server configuration from `~/.config/agent-loop/mcp.json`.
- For each server, it starts a session and lists available services.
- Each service is registered as a tool (named `<server>-<service>`) and can be called by the agent or user.
- All MCP tools are available alongside built-in tools.

### Example MCP config

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "..." }
    },
    "mcp-obsidian": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian", "/path/to/obsidian-vault/"]
    }
  }
}
```

- Place this file at `~/.config/agent-loop/mcp.json`.
- Each server can be a local or remote MCP-compatible service.
- All services/tools from these servers will be available in your agent session.
- For more details, see the [Cursor MCP documentation](https://docs.cursor.com/context/model-context-protocol#configuring-mcp-servers).

---

## Available Tools

Agent Loop comes with built-in tools and supports custom tools. The application automatically distinguishes between different tool types with visual indicators:

- **🛠️ Built-in Tools**: Core application tools
- **🔌 MCP Tools**: External tools from Model Context Protocol servers
- **🔧 Custom Tools**: User-defined tools loaded from `~/.config/agent-loop/tools/`

On startup, Agent Loop will display any custom tools that have been loaded:

```
🔧 [Custom Tools] Loaded 2 custom tool(s) from ~/.config/agent-loop/tools:
  • hello (hello.py) - Returns a friendly greeting
  • my_tool (my_tool.py) - Custom automation tool
```

| Tool                  | Description                                                     |
| --------------------- | --------------------------------------------------------------- |
| **bash**              | Execute bash commands                                           |
| **python**            | Evaluate Python code in a sandboxed subprocess                  |
| **node**              | Evaluate Node.js code in a sandboxed subprocess                 |
| **sympy**             | Perform symbolic mathematics operations using SymPy             |
| **filesystem**        | Read, create, update, append, delete files with UTF-8 encoding  |
| **http**              | Make HTTP requests using HTTPie with easy JSON handling         |
| **curl**              | Make HTTP requests using curl                                   |
| **git**               | Run Git commands in the current repository                      |
| **docker**            | Run Docker CLI commands                                         |
| **project_inspector** | Inspect the current project directory and preview source files  |
| **kubectl**           | Run kubectl commands to interact with a Kubernetes cluster      |
| **aws_cli**           | Run AWS CLI v2 read-only commands to interact with AWS services |
| **jira**              | Query JIRA via REST API using safe, read-only endpoints         |
| **confluence**        | Query Atlassian Confluence Cloud via REST API (read-only)       |
| **MCP**               | All services from configured MCP servers (see above)            |
| **Custom**            | User-defined tools from `~/.config/agent-loop/tools/`           |

See [Creating Tools Guide](CREATING_TOOLS.md) for instructions on how to create your own tools.

---

## Installation

### Option 1: Using the installation script (Recommended)

1. **Download the installation package:**

   ```sh
   git clone https://github.com/your-org/agent-loop.git
   cd agent-loop
   ```

2. **Run the installation script:**

   ```sh
   ./install.sh
   ```

   This script will:

   - Create a virtual environment at `~/.local/share/agent-loop/venv`
   - Install all required dependencies
   - Install the agent-loop package
   - Create a command wrapper at `~/.local/bin/agent-loop`

3. **Add to your PATH (if needed):**

   ```sh
   echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Option 2: Manual installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/your-org/agent-loop.git
   cd agent-loop
   ```

2. **Install dependencies:**

   Using [uv](https://astral.sh/uv), a much faster Python package manager:

   ```sh
   uv pip install -r requirements.txt
   ```

   If you don't have uv installed, you can install it with:

   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### Uninstalling

To uninstall Agent Loop, simply run:

```sh
./install.sh uninstall
```

This will remove the command wrapper and the virtual environment.

### Windows Subsystem for Linux (WSL) Installation

Agent Loop works great on Windows through WSL. Here's how to set it up:

1. **Install WSL if you don't have it already**:

   - Open PowerShell as Administrator and run:

     ```powershell
     wsl --install
     ```

   - Restart your computer after installation completes
   - For detailed instructions, see [Microsoft's WSL installation guide](https://docs.microsoft.com/en-us/windows/wsl/install)

2. **Install Agent Loop in WSL**:

   - Open your WSL terminal
   - Follow the same installation instructions as above:

     ```sh
     git clone https://github.com/your-org/agent-loop.git
     cd agent-loop
     ./install.sh
     ```

3. **Configuration in WSL**:

   - Create the config directory in your WSL home:

     ```sh
     mkdir -p ~/.config/agent-loop
     ```

   - Add your API keys to `.env` file:

     ```sh
     nano ~/.config/agent-loop/.env
     ```

   - Optional: Add a custom system prompt:

     ```sh
     nano ~/.config/agent-loop/SYSTEM_PROMPT.txt
     ```

4. **WSL-specific considerations**:
   - The agent-loop can access both Linux and Windows files
   - Windows files are mounted at `/mnt/c/`, `/mnt/d/`, etc.
   - To access Windows directories, use paths like `/mnt/c/Users/YourName/Documents`
   - For best performance, keep your projects within the WSL filesystem

## Configuration

### API Keys and Environment Variables

Create a `.env` file in the `~/.config/agent-loop` directory with your API keys and other configuration:

```sh
# Create the config directory if it doesn't exist
mkdir -p ~/.config/agent-loop

# Create your .env file
nano ~/.config/agent-loop/.env
```

You can also create a local `.env` file in your project directory, which will take priority over the global configuration.

You can use the `.env.example` file from the source repository as a template. At minimum, include one of these API keys:

```text
# AI Configuration
AI_PROVIDER=anthropic  # Choose: anthropic (default) or openai
AI_TEMPERATURE=0.7     # Model temperature: 0.0-2.0 (default: 0.7)

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-3-7-sonnet-latest  # Optional, defaults to claude-3-7-sonnet-latest

# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o

# Jira (Optional)
JIRA_BASE_URL=your_jira_instance_url
JIRA_EMAIL=your_jira_email
JIRA_API_TOKEN=your_jira_api_token

# Confluence (Optional)
CONFLUENCE_BASE_URL=your_confluence_instance_url
CONFLUENCE_EMAIL=your_confluence_email
CONFLUENCE_API_TOKEN=your_confluence_api_token
```

**Configuration Priority:**

- Local `.env` file in your current directory (highest priority)
- Global `.env` file in `~/.config/agent-loop/` (fallback)

**AI Provider Selection:**

- Set `AI_PROVIDER=anthropic` to use Claude models (default)
- Set `AI_PROVIDER=openai` to use GPT models
- If the preferred provider's API key is missing, the application will automatically fall back to the available provider

**Temperature Control:**

- `AI_TEMPERATURE` controls response creativity and randomness (0.0 = deterministic, 1.0 = creative)
- Valid range: 0.0 to 2.0
- Default: 0.7 (balanced)

### Custom System Prompt

You can customize the system prompt by creating a `SYSTEM_PROMPT.txt` file in the same directory:

```sh
nano ~/.config/agent-loop/SYSTEM_PROMPT.txt
```

This allows you to give specific instructions or personality to the assistant. If this file doesn't exist, the default system prompt will be used.

### MCP Server Configuration

To enable MCP integration, create a file at `~/.config/agent-loop/mcp.json` as shown above. Each server entry should specify the command, arguments, and any required environment variables. All services from these servers will be available as tools in your agent session.

## Usage

### Basic

```sh
agent-loop
```

### Model Selection

```sh
agent-loop --model gpt-4o
```

or

```sh
agent-loop --model claude-3-7-sonnet-latest
```

### Safe Mode (Human Confirmation)

```sh
agent-loop --safe
```

- You will be shown each command and asked to confirm before execution.

### Debug Mode

```sh
agent-loop --debug
```

- Prints tool input/output for transparency.

### Combined

```sh
agent-loop --safe --debug
```

---

## Example Session

```bash
dev@agent-loop:~$ agent-loop --safe
> List all Docker containers
Agent: I will use the docker tool to list all containers.
[CONFIRMATION REQUIRED]
Tool: docker
Description: Run Docker CLI commands
Input: {'args': 'ps -a'}
Do you want to execute this command? [y/N]: y
STDOUT:
CONTAINER ID   IMAGE   ...
```

## ✨ Beautiful, Themeable CLI Output

Agent Loop uses [Rich](https://rich.readthedocs.io/) to render all agent replies and notifications in the terminal. By default, all agent answers are formatted in **Markdown** and rendered with color, style, and structure for maximum readability.

- **Default:** Answers are rendered as Markdown (headings, lists, code blocks, etc.)
- **Theming:** Colors and styles are fully customizable via a JSON theme file
- **Plain Text Mode:** Use `--simple-text` or `-s` to disable Rich/Markdown and get pure ASCII output (great for piping or minimal terminals)

### Example (Markdown Output)

```bash
💬 Agent:
# Docker Containers

| CONTAINER ID | IMAGE | STATUS |
|--------------|-------|--------|
| 123abc       | nginx | Up     |
| ...          | ...   | ...    |
```

### Example (Plain Text Output)

```bash
💬 Agent:
Docker Containers
----------------
CONTAINER ID   IMAGE   STATUS
123abc         nginx   Up
...            ...     ...
```

---

## 🎨 Customizing the Theme

You can fully customize the CLI appearance by editing the theme file:

- **Location:** `~/.config/agent-loop/theme.json`
- **Format:** JSON mapping style names to Rich style strings
- **Fallback:** If the file is missing or invalid, a beautiful default theme is used

**Example `theme.json`:**

```json
{
  "agent.reply": "bold cyan",
  "agent.tool": "bold magenta",
  "agent.confirm": "bold yellow",
  "agent.error": "bold red",
  "agent.info": "dim white"
}
```

Change colors, add emphasis, or create your own style! See the [Rich style guide](https://rich.readthedocs.io/en/latest/style.html) for options.

---

## 🚀 CLI Flags

| Flag                  | Description                                                       |
| --------------------- | ----------------------------------------------------------------- |
| `--simple-text`, `-s` | Output plain ASCII text (no Rich, no Markdown)                    |
| `--safe`              | Require confirmation before executing any tool                    |
| `--debug`             | Show tool input/output for transparency                           |
| `--model`             | Select the LLM model (e.g., `gpt-4o`, `claude-3-7-sonnet-latest`) |

---

## 🛠️ Creating Your Own Tools

Agent Loop is fully extensible! You can add your own tools in minutes—no need to modify the core code.

- **Drop-in Python modules** (pure functions, functional programming style)
- **Auto-discovered**: Just place your `.py` file in `agent_loop/tools/` (built-in) or `~/.config/agent-loop/tools/` (user tools)
- **No extra dependencies** for user tools—see the policy in the guide

👉 **See the full guide:** [CREATING_TOOLS.md](CREATING_TOOLS.md)

## License

This project is licensed under the GNU Affero General Public License v3.0,
with additional terms prohibiting commercial use and requiring attribution.

See [LICENSE](./LICENSE) for full details.
