import sys

from mini_agentloop import run_agent


def main():
    if len(sys.argv) < 2:
        print('Usage: mini-agentloop "<task>" [workspace_path]')
        print('Example: mini-agentloop "List all Python files in this project" .')
        sys.exit(1)

    task = sys.argv[1]
    workspace = sys.argv[2] if len(sys.argv) > 2 else ""

    print(f"[Task] {task}")
    if workspace:
        print(f"[Workspace] {workspace}")

    result = run_agent(task, workspace)
    print(f"\n{'='*60}")
    print("[Result]")
    print(result)


if __name__ == "__main__":
    main()
