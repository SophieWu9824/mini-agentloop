# python3 main.py "你的任务描述" [工作区路径]

# # 示例
# python3 main.py "看看这个目录下有哪些文件，读一下 config.py 的内容"
# python3 main.py "帮我分析这个项目的结构" /path/to/project

import sys
from agent import run_agent


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<task>\" [workspace_path]")
        print("Example: python main.py \"List all Python files in this project\" .")
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
