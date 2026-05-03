import os
import subprocess

MAX_OUTPUT_LEN = 3000

SAFE_COMMANDS = {
    "ls", "dir", "cat", "head", "tail", "find", "grep", "wc",
    "pwd", "echo", "whoami", "which", "type",
    "git status", "git log", "git diff", "git branch",
    "npm test", "pytest", "python -m pytest", "go test",
    "ruff check", "mypy", "flake8", "black --check",
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at the given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the content of a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command. Only whitelisted safe commands are allowed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute.",
                    }
                },
                "required": ["command"],
            },
        },
    },
]


def _trim_output(text: str) -> str:
    if len(text) <= MAX_OUTPUT_LEN:
        return text
    return text[:MAX_OUTPUT_LEN] + f"\n... [truncated, {len(text)} chars total]"


def _is_command_allowed(command: str) -> bool:
    cmd_stripped = command.strip()
    for safe in SAFE_COMMANDS:
        if cmd_stripped == safe or cmd_stripped.startswith(safe + " "):
            return True
    return False


def _resolve_path(path: str) -> str:
    return os.path.abspath(path)


def list_files(path: str) -> str:
    resolved = _resolve_path(path)
    if not os.path.isdir(resolved):
        return f"Error: '{resolved}' is not a directory."
    try:
        entries = os.listdir(resolved)
        if not entries:
            return "(empty directory)"
        lines = []
        for entry in sorted(entries):
            full = os.path.join(resolved, entry)
            prefix = "[DIR]  " if os.path.isdir(full) else "[FILE] "
            lines.append(prefix + entry)
        return _trim_output("\n".join(lines))
    except PermissionError:
        return f"Error: Permission denied for '{resolved}'."
    except Exception as e:
        return f"Error: {e}"


def read_file(path: str) -> str:
    resolved = _resolve_path(path)
    if not os.path.isfile(resolved):
        return f"Error: '{resolved}' is not a file."
    try:
        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return _trim_output(content)
    except PermissionError:
        return f"Error: Permission denied for '{resolved}'."
    except Exception as e:
        return f"Error: {e}"


def run_command(command: str) -> str:
    if not _is_command_allowed(command):
        return f"Error: Command not in whitelist: '{command}'. Allowed prefixes: {', '.join(sorted(SAFE_COMMANDS))}"
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            if output:
                output += "\n"
            output += "[STDERR] " + result.stderr
        if not output:
            output = "(no output)"
        return _trim_output(output)
    except subprocess.TimeoutExpired:
        return "Error: Command timed out (30s limit)."
    except Exception as e:
        return f"Error: {e}"


TOOL_EXECUTORS = {
    "list_files": list_files,
    "read_file": read_file,
    "run_command": run_command,
}


def execute_tool(name: str, arguments: dict) -> str:
    executor = TOOL_EXECUTORS.get(name)
    if not executor:
        return f"Error: Unknown tool '{name}'."
    try:
        return executor(**arguments)
    except TypeError as e:
        return f"Error: Invalid arguments for '{name}': {e}"
    except Exception as e:
        return f"Error: Tool execution failed for '{name}': {e}"
