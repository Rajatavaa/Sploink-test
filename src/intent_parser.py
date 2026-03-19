import json


async def parse_intent(user_input: str) -> dict:
    """
    Rule-based intent parser.
    Maps user input to task types.
    """
    user_input_lower = user_input.lower()

    intent_map = {
        "summarization": ["summarize", "summary", "summarizing", "brief"],
        "question_answering": [
            "research",
            "find",
            "answer",
            "question",
            "what is",
            "who is",
            "how to",
            "tell me",
            "explain",
            "describe",
            "about",
        ],
        "math": [
            "calculate",
            "math",
            "compute",
            "evaluate",
            "solve",
            "+",
            "-",
            "*",
            "/",
            "**",
        ],
        "content_generation": ["write", "generate", "create", "draft", "compose"],
    }

    for capability, keywords in intent_map.items():
        for keyword in keywords:
            if keyword in user_input_lower:
                return {
                    "task_type": capability,
                    "confidence": 1.0,
                    "raw_input": user_input,
                }

    return {"task_type": "general", "confidence": 0.3, "raw_input": user_input}


def load_registry(registry_path: str = "register.json") -> list:
    """Load agent registry from JSON file."""
    try:
        with open(registry_path, "r") as f:
            data = json.load(f)
            return data.get("agents", [])
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
