# Agent Loop

> **An AI Agent with optional Human-in-the-Loop Safety**

---

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Anthropic](https://img.shields.io/badge/Anthropic-API-orange)

### Tools

![Bash](https://img.shields.io/badge/Tool-Bash-black?logo=gnu-bash)
![Python](https://img.shields.io/badge/Tool-Python-3776AB?logo=python)
![Curl](https://img.shields.io/badge/Tool-Curl-073551?logo=curl)
![Git](https://img.shields.io/badge/Tool-Git-F05032?logo=git)
![Docker](https://img.shields.io/badge/Tool-Docker-2496ED?logo=docker)
![Project Inspector](https://img.shields.io/badge/Tool-Project_Inspector-lightgrey)
![Kubectl](https://img.shields.io/badge/Tool-Kubectl-326CE5?logo=kubernetes)
![AWS CLI](https://img.shields.io/badge/Tool-AWS_CLI-232F3E?logo=amazon-aws)
![Jira](https://img.shields.io/badge/Tool-Jira-0052CC?logo=jira)
![Confluence](https://img.shields.io/badge/Tool-Confluence-172B4D?logo=confluence)
![Home Assistant](https://img.shields.io/badge/Tool-Home_Assistant-41BDF5?logo=home-assistant)

---

## Overview

**Agent Loop** is a command-line AI assistant. It leverages Anthropic's Claude models and a suite of powerful tools to automate, inspect, and manage your development environment—while keeping you in control with optional human confirmation for every action.

- **Human-in-the-Loop:** Add `--safe` to require confirmation before any tool runs.
- **Functional Programming:** Clean, composable, and testable code.
- **DevOps Ready:** Integrates with Bash, Python, Docker, Git, Kubernetes, AWS, and more.

---

## Features

- Conversational AI agent powered by Anthropic Claude
- Tool execution with optional human confirmation (`--safe` mode)
- Debug mode for transparency (`--debug`)
- Modular, extensible tool system
- Functional programming style throughout

---

## Available Tools

| Tool                  | Description                                                     |
| --------------------- | --------------------------------------------------------------- |
| **bash**              | Execute bash commands                                           |
| **python**            | Evaluate Python code in a sandboxed subprocess                  |
| **curl**              | Make HTTP requests using curl                                   |
| **git**               | Run Git commands in the current repository                      |
| **docker**            | Run Docker CLI commands                                         |
| **project_inspector** | Inspect the current project directory and preview source files  |
| **kubectl**           | Run kubectl commands to interact with a Kubernetes cluster      |
| **aws_cli**           | Run AWS CLI v2 read-only commands to interact with AWS services |
| **jira**              | Query JIRA via REST API using safe, read-only endpoints         |
| **confluence**        | Query Atlassian Confluence Cloud via REST API (read-only)       |
| **home_assistant**    | Control and query devices in your Home Assistant setup          |

---

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/your-org/agent-loop.git
   cd agent-loop
   ```

2. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Basic

```sh
python main.py
```

### Safe Mode (Human Confirmation)

```sh
python main.py --safe
```

- You will be shown each command and asked to confirm before execution.

### Debug Mode

```sh
python main.py --debug
```

- Prints tool input/output for transparency.

### Combined

```sh
python main.py --safe --debug
```

---

## Example Session

```bash
dev@agent-loop:~$ List all Docker containers
Agent: I will use the docker tool to list all containers.
[CONFIRMATION REQUIRED]
Tool: docker
Description: Run Docker CLI commands
Input: {'args': 'ps -a'}
Do you want to execute this command? [y/N]: y
STDOUT:
CONTAINER ID   IMAGE   ...
```
