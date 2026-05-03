import json

from config import call_model
from tools import TOOL_DEFINITIONS, execute_tool
from memory import load_context, save_observation

MAX_STEPS = 8
MAX_TOOL_CALLS = 20

SYSTEM_PROMPT = """You are a minimal coding agent. You can explore the codebase using the provided tools.

Workflow:
1. Understand the user's task.
2. Use list_files and read_file to explore the codebase.
3. Use run_command to run safe commands (tests, lint, etc.) when needed.
4. When you have enough information, provide a clear answer.

Rules:
- Always explore before answering.
- Be concise in your observations.
- If a tool returns an error, report it and try a different approach.
- When done, provide a summary of what you found and what you did.
- You have a maximum of {max_steps} steps. Each tool call counts as one step.
- Plan your exploration: reserve the last 1-2 steps for your final answer.
- You will be told the current step number at each turn."""


def run_agent(task: str, workspace: str = "") -> str:
    messages = load_context(workspace)
    messages.append({"role": "system", "content": SYSTEM_PROMPT.format(max_steps=MAX_STEPS)})
    messages.append({"role": "user", "content": task})

    tool_call_count = 0

    for step in range(MAX_STEPS):
        step_info = f"[Step {step + 1}/{MAX_STEPS}]"
        print(f"\n--- {step_info} ---")

        messages.append({"role": "user", "content": step_info})

        response = call_model(messages, tools=TOOL_DEFINITIONS)

        messages.append(response.to_dict())

        if not response.tool_calls:
            print(f"\n[Agent] {response.content}")
            save_observation("final_answer", response.content)
            return response.content

        for tool_call in response.tool_calls:
            tool_call_count += 1
            if tool_call_count > MAX_TOOL_CALLS:
                msg = f"Stopped: tool call limit ({MAX_TOOL_CALLS}) reached."
                print(f"\n[Harness] {msg}")
                return msg

            fn_name = tool_call.function.name
            try:
                fn_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                fn_args = {}

            print(f"  [Tool Call] {fn_name}({fn_args})")

            observation = execute_tool(fn_name, fn_args)
            print(f"  [Observation] {observation[:200]}{'...' if len(observation) > 200 else ''}")

            save_observation(f"tool:{fn_name}", observation)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": observation,
            })

    msg = f"Stopped: step limit ({MAX_STEPS}) reached."
    print(f"\n[Harness] {msg}")
    return msg
