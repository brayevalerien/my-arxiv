import argparse
import os
import sys
from argparse import Namespace

from commands import CommandHandler


def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser(prog="my-arxiv", description="Manage academic papers using the Arxiv API.")

    parser.add_argument("command", help="Command to run: search, later, read, done, info, or list")
    parser.add_argument("command_args", nargs="*", help="Arguments passed to the command")

    return parser.parse_args()


def main():
    args = parse_arguments()
    command = args.command.lower()
    command_args = args.command_args
    
    handler = CommandHandler()
    
    try:
        if command == "search":
            if not command_args:
                print("Usage: my-arxiv search <query> [max_results]")
                return 1
            query = command_args[0]
            max_results = int(command_args[1]) if len(command_args) > 1 else 10
            handler.search(query, max_results)
            
        elif command == "later":
            if not command_args:
                print("Usage: my-arxiv later <arxiv_id>")
                return 1
            arxiv_id = command_args[0]
            handler.later(arxiv_id)
            
        elif command == "read":
            if not command_args:
                print("Usage: my-arxiv read <arxiv_id>")
                return 1
            arxiv_id = command_args[0]
            handler.read(arxiv_id)
            
        elif command == "done":
            if not command_args:
                print("Usage: my-arxiv done <arxiv_id>")
                return 1
            arxiv_id = command_args[0]
            handler.done(arxiv_id)
            
        elif command == "info":
            if not command_args:
                print("Usage: my-arxiv info <arxiv_id>")
                return 1
            arxiv_id = command_args[0]
            handler.info(arxiv_id)
            
        elif command == "list":
            status = command_args[0] if command_args else None
            handler.list_papers(status)
            
        else:
            print(f"Unrecognized command: {command}")
            print("Available commands: search, later, read, done, info, list")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
