# Agent Loop

> **An AI Agent with optional Human-in-the-Loop Safety and Model Context Protocol (MCP) integration**

---

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![uv](https://img.shields.io/badge/uv-Package_Manager-7c4dff)
![Anthropic](https://img.shields.io/badge/Anthropic-API-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-API-green?logo=openai)
![MCP](https://img.shields.io/badge/Tool-MCP-4B8BBE?logo=protocols)
**![Version](https://img.shields.io/badge/version-2.0.0-blue)**

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

- [Agent Loop](#agent-loop)
  - [Tools](#tools)
  - [Overview](#overview)
  - [Features](#features)
  - [MCP (Model Context Protocol) Integration](#mcp-model-context-protocol-integration)
    - [How it works](#how-it-works)
    - [Example MCP config](#example-mcp-config)
  - [Available Tools](#available-tools)
  - [Installation](#installation)
    - [Option 1: Using the installation script (Recommended)](#option-1-using-the-installation-script-recommended)
    - [Option 2: Manual installation](#option-2-manual-installation)
    - [Uninstalling](#uninstalling)
    - [Windows Subsystem for Linux (WSL) Installation](#windows-subsystem-for-linux-wsl-installation)
  - [Configuration](#configuration)
    - [API Keys and Environment Variables](#api-keys-and-environment-variables)
    - [Custom System Prompt](#custom-system-prompt)
    - [MCP Server Configuration](#mcp-server-configuration)
  - [Usage](#usage)
    - [Basic](#basic)
    - [Model Selection](#model-selection)
    - [Safe Mode (Human Confirmation)](#safe-mode-human-confirmation)
    - [Debug Mode](#debug-mode)
    - [Combined](#combined)
  - [Example Session](#example-session)
  - [License](#license)

## Overview

**Agent Loop** is a command-line AI assistant. It leverages Anthropic's Claude or OpenAI's GPT models and a suite of powerful tools to automate, inspect, and manage your development environment—while keeping you in control with optional human confirmation for every action.

- **Human-in-the-Loop:** Add `--safe` to require confirmation before any tool runs.
- **Functional Programming:** Clean, composable, and testable code.
- **DevOps Ready:** Integrates with Bash, Python, Docker, Git, Kubernetes, AWS, and more.
- **Multi-Provider:** Supports both Anthropic Claude and OpenAI GPT models.
- **MCP Integration:** Dynamically loads and uses tools/services from any MCP-compatible server (see below).

---

## Features

- Conversational AI agent powered by Anthropic Claude or OpenAI GPT
- Tool execution with optional human confirmation (`--safe` mode)
- Debug mode for transparency (`--debug`)
- Modular, extensible tool system
- Functional programming style throughout
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

You can use the `.env.example` file from the source repository as a template. At minimum, include one of these API keys:

```text
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

If both Anthropic and OpenAI API keys are set, Anthropic Claude will be used by default.

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

## License

This project is licensed under the GNU Affero General Public License v3.0,
with additional terms prohibiting commercial use and requiring attribution.

See [LICENSE](./LICENSE) for full details.
