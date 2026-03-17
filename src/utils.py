import json
from datetime import datetime


def load_json(filepath: str) -> dict:
    """Load JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_json(filepath: str, data: dict) -> bool:
    """Save data to JSON file."""
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def log_message(level: str, message: str) -> None:
    """Simple logging function."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level.upper()}] {message}")


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50 + "\n")


def print_result(result: str) -> None:
    """Print formatted result."""
    print("\n--- Result ---")
    print(result)
    print("--------------\n")


def get_user_input() -> str:
    """Get user input from CLI."""
    return input("Enter your request: ").strip()
