import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intent_parser import parse_intent, load_registry
from router import route_with_logging
from agent import execute_agent
from utils import print_header, print_result, log_message, get_user_input


def main():
    print_header("AI Agent System")

    print(
        "Welcome! This is an AI agent system that routes your requests to appropriate agents."
    )
    print(
        "Available capabilities: summarization, question_answering, math, content_generation"
    )
    print("\nType 'exit' or 'quit' to end the session.\n")

    while True:
        user_input = get_user_input()

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            print("Please enter a valid request.\n")
            continue

        log_message("info", f"User input: {user_input}")

        intent = parse_intent(user_input)
        log_message(
            "info",
            f"Parsed intent: {intent.get('task_type')} (confidence: {intent.get('confidence')})",
        )

        agents = load_registry()
        if not agents:
            print("Error: No agents found in registry.")
            continue

        selected_agent = route_with_logging(intent, agents)

        if not selected_agent:
            print(f"\nSorry, I couldn't find an agent to handle: {user_input}\n")
            continue

        print(f"\nExecuting {selected_agent.get('name')}...")

        result = execute_agent(selected_agent, user_input)

        print_result(result)


if __name__ == "__main__":
    main()
