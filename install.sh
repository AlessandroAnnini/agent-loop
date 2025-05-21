#!/bin/bash
set -e

# Uninstall functionality
if [ "$1" = "uninstall" ]; then
  echo "Uninstalling agent-loop..."
  rm -f ~/.local/bin/agent-loop
  rm -rf ~/.local/share/agent-loop
  echo "agent-loop has been uninstalled."
  exit 0
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv ~/.local/share/agent-loop/venv

# Install dependencies
echo "Installing dependencies..."
~/.local/share/agent-loop/venv/bin/pip install anthropic openai python-dotenv sympy halo requests

# Install the agent-loop package
echo "Installing agent-loop..."
~/.local/share/agent-loop/venv/bin/pip install .

# Create a wrapper script
echo "Creating command wrapper..."
mkdir -p ~/.local/bin
cat > ~/.local/bin/agent-loop << 'WRAPPER'
#!/bin/bash
~/.local/share/agent-loop/venv/bin/agent-loop "$@"
WRAPPER

chmod +x ~/.local/bin/agent-loop

echo "Installation complete!"
echo "Make sure ~/.local/bin is in your PATH."
echo "You can now run 'agent-loop' to use the tool."


