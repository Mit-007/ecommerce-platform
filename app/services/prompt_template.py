from pathlib import Path
from jinja2 import Template
from app.core.logger import logger
from app.core.constant import company , dateTime
from app.core.config import PROMPT_FILE_PATH

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
    
    try:
        if not PROMPT_FILE_PATH.exists():
            raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE_PATH}")
        
        logger.info(f"Loading prompt template from {PROMPT_FILE_PATH}")
        prompt_text = PROMPT_FILE_PATH.read_text(encoding="utf-8")
        
        if not prompt_text or not prompt_text.strip():
            raise ValueError("Prompt template is empty")
        
        _chat_agent_template = Template(prompt_text)
        logger.info("Prompt templates initialized successfully")
    
    except FileNotFoundError as e:
        logger.error(f"Failed to load prompt template: {e}")
        raise RuntimeError(f"Prompt template file missing: {e}") from e
    
    except Exception as e:
        logger.error(f"Failed to initialize prompt templates: {e}", exc_info=True)
        raise RuntimeError(f"Failed to initialize prompts: {e}") from e


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
        dateTime = dateTime,
        company = company,
        question=question,
        previous_chat=previous_chat,
        tool_call_log=tool_call_log,
    )