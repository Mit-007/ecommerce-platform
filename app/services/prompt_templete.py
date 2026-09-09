from pathlib import Path
from jinja2 import Template
from app.core.logger import logger
from app.core.constant import company

# ============================================================
# Prompt configuration
# ============================================================

PROMPT_PATH = Path("app/agent/prompts/support_agent_prompt.md")

# ============================================================
# Prompt initialization
# ============================================================

_chat_agent_template: Template | None = None


def initialize_prompt_templates() -> None:
    """
    Load and compile the chat agent prompt once.

    This should be called during application startup.
    """
    global _chat_agent_template
    
    prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
    
    _chat_agent_template = Template(prompt_text)


# ============================================================
# Prompt rendering
# ============================================================

def get_chat_agent_prompt(
    question: str,
    previous_chat: list[dict],
    tool_call_log: list[dict]
) -> str:
    """
    Render the initialized chat agent prompt
    using runtime data.
    """

    if _chat_agent_template is None:
        raise RuntimeError(
            "Chat agent prompt is not initialized. "
            "Call initialize_prompt_templates() first."
        )

    return _chat_agent_template.render(
        company = company,
        question=question,
        previous_chat=previous_chat,
        tool_call_log=tool_call_log,
    )