import sys
import os
import requests
import time
import argparse
from typing import Optional

BASE_URL = "http://localhost:5137"


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def submit_request(text: str) -> Optional[str]:
    """Submit a new request to the server."""
    try:
        response = requests.post(f"{BASE_URL}/request", json={"text": text})
        response.raise_for_status()
        data = response.json()
        print(f"✓ Request submitted: {data['request_id']}")
        print(f"  Status: {data['status']}")
        print(f"  Message: {data['message']}")
        return data["request_id"]
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to server. Is it running?")
        print("  Run: python server.py")
        return None
    except requests.exceptions.RequestException as e:
        print(f"✗ Error submitting request: {e}")
        return None


def check_request(request_id: str, poll: bool = False, interval: float = 0.5):
    """Check the status/result of a request."""
    try:
        response = requests.get(f"{BASE_URL}/request/{request_id}")
        response.raise_for_status()
        data = response.json()

        print(f"\nRequest {request_id}:")
        print(f"  Status: {data['status']}")
        print(f"  Input: {data['input_text']}")

        if data["status"] == "processing":
            print(f"  ⏳ Processing...")
            if poll:
                time.sleep(interval)
                check_request(request_id, poll=True, interval=interval)
            return

        if data["error"]:
            print(f"  Error: {data['error']}")

        if data["result"]:
            print(f"\n{'─' * 60}")
            print(f"RESULT:")
            print(f"{'─' * 60}")
            print(data["result"])

        if data["processing_time"]:
            print(f"\n{'─' * 60}")
            print(f"Processing time: {data['processing_time']:.2f}s")

    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to server.")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error checking request: {e}")


def list_requests(status: Optional[str] = None):
    """List all requests."""
    try:
        params = {"status": status} if status else {}
        response = requests.get(f"{BASE_URL}/requests", params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            print("No requests found.")
            return

        print(f"\nTotal requests: {len(data)}")
        if status:
            print(f"Filtered by status: {status}")
        print()

        for req in data:
            status_icon = {
                "queued": "⏳",
                "processing": "⚙️",
                "completed": "✓",
                "failed": "✗",
            }.get(req["status"], "?")

            print(
                f"{status_icon} [{req['request_id']}] {req['status']:12} | {req['input_text'][:50]}"
            )

    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to server.")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error listing requests: {e}")


def health_check():
    """Check server health."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()

        print("\n🟢 Server Health:")
        print(f"  Status: {data['status']}")
        print(f"  Timestamp: {data['timestamp']}")
        print(f"  Active requests: {data['active_requests']}")
        print(f"  Total requests: {data['total_requests']}")
        print(f"  Agents loaded: {data['agents_loaded']}")

    except requests.exceptions.ConnectionError:
        print("🔴 Server is offline")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}")


def interactive_mode():
    """Run in interactive mode."""
    print_header("AI Agent System - Client")
    print("Commands:")
    print("  submit <text>  - Submit a new request")
    print("  check <id>    - Check request status/result")
    print("  poll <id>      - Poll until request completes")
    print("  list           - List all requests")
    print(
        "  list <status>  - List requests by status (queued/processing/completed/failed)"
    )
    print("  health         - Check server health")
    print("  clear          - Clear completed/failed requests")
    print("  quit           - Exit\n")

    while True:
        try:
            user_input = input("> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            parts = user_input.split(None, 1)
            command = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None

            if command == "submit" and arg:
                request_id = submit_request(arg)
                if request_id:
                    print(f"\nChecking status in 1 second...")
                    time.sleep(1)
                    check_request(request_id, poll=True, interval=1)

            elif command == "check" and arg:
                check_request(arg)

            elif command == "poll" and arg:
                print(f"\nPolling request {arg}... (Ctrl+C to stop)")
                try:
                    check_request(arg, poll=True, interval=1)
                except KeyboardInterrupt:
                    print("\nStopped polling.")

            elif command == "list":
                list_requests(arg)

            elif command == "health":
                health_check()

            elif command == "clear":
                try:
                    response = requests.post(f"{BASE_URL}/clear")
                    response.raise_for_status()
                    print(f"\n✓ {response.json()['message']}")
                    print(f"  Remaining: {response.json()['remaining_requests']}")
                except Exception as e:
                    print(f"✗ Error: {e}")

            else:
                print("Unknown command. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="AI Agent System - Client")
    parser.add_argument(
        "command",
        nargs="?",
        help="Command to run (submit, check, poll, list, health, clear)",
    )
    parser.add_argument("argument", nargs="?", help="Argument for the command")
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--url", default=BASE_URL, help=f"API base URL (default: {BASE_URL})"
    )

    args = parser.parse_args()

    if args.url != BASE_URL:
        globals()["BASE_URL"] = args.url

    if args.interactive or not args.command:
        interactive_mode()
    else:
        command = args.command.lower()
        arg = args.argument

        if command == "submit" and arg:
            request_id = submit_request(arg)
            if request_id:
                print(f"\nCheck status with: python client.py check {request_id}")

        elif command == "check" and arg:
            check_request(arg)

        elif command == "poll" and arg:
            check_request(arg, poll=True, interval=1)

        elif command == "list":
            list_requests(arg)

        elif command == "health":
            health_check()

        elif command == "clear":
            try:
                response = requests.post(f"{BASE_URL}/clear")
                response.raise_for_status()
                print(f"\n✓ {response.json()['message']}")
                print(f"  Remaining: {response.json()['remaining_requests']}")
            except Exception as e:
                print(f"✗ Error: {e}")

        else:
            parser.print_help()


if __name__ == "__main__":
    main()
