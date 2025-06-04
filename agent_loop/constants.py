"""
Constants for agent-loop CLI application.
Contains format instructions and user-facing messages.
"""

# LLM format instructions
PLAIN_FORMAT_INSTRUCTION = "(Format your answer as plain ASCII text, optimized for CLI readability. Do not use markdown or special formatting.)"
MARKDOWN_FORMAT_INSTRUCTION = "(Format your answer using markdown syntax. Use markdown features for clarity and readability in a terminal that supports markdown rendering.)"

# User interface messages
HELP_MESSAGE = "[AgentLoop] Press CTRL+C to interrupt and return to prompt. Press CTRL+D or type 'exit'/'quit' to quit.\n"
