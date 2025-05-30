import subprocess
import tempfile
import os

tool_definition = {
    "name": "python",
    "description": "Evaluate Python code in a sandboxed subprocess",
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to evaluate"}
        },
        "required": ["code"],
    },
}


def handle_call(input_data):
    code = input_data["code"]

    try:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        # Run the code in a subprocess
        result = subprocess.run(
            ["python3", temp_path], capture_output=True, text=True, timeout=5
        )

        os.remove(temp_path)

        return (
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
            f"EXIT CODE: {result.returncode}"
        )
    except subprocess.TimeoutExpired:
        return "Python code execution timed out."
    except Exception as e:
        return f"Error executing sandboxed Python: {e}"
