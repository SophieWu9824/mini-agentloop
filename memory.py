import os
from datetime import datetime

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")


def _ensure_memory_dir():
    os.makedirs(MEMORY_DIR, exist_ok=True)


def load_context(workspace: str = "") -> list:
    messages = []

    agents_md = os.path.join(workspace, "AGENTS.md") if workspace else ""
    if agents_md and os.path.isfile(agents_md):
        with open(agents_md, "r", encoding="utf-8") as f:
            messages.append({"role": "system", "content": f"[Project Rules]\n{f.read()}"})

    summary_path = os.path.join(MEMORY_DIR, "session-summary.md")
    if os.path.isfile(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content:
            messages.append({"role": "system", "content": f"[Session Summary]\n{content}"})

    return messages


def save_observation(role: str, content: str):
    _ensure_memory_dir()
    log_path = os.path.join(MEMORY_DIR, "session-log.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n## [{timestamp}] {role}\n{content}\n")


def save_summary(summary: str):
    _ensure_memory_dir()
    summary_path = os.path.join(MEMORY_DIR, "session-summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
