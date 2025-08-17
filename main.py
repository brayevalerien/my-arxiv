import argparse
import os
from argparse import Namespace


def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser(prog="my-arxiv", description="Manage academic papers using the Arxiv API.")

    parser.add_argument("command", help="Command to run, can be later, read, done, search or info.")
    parser.add_argument("command_args", nargs="*", help="Arguments passed to the command.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    command = args.command.lower()

    print(f'Running "{command}" with arguments [{", ".join(args.command_args)}]')  # debug
    if command == "later":
        raise NotImplementedError('Command "later" is not implemented yet.')
    elif command == "read":
        raise NotImplementedError('Command "read" is not implemented yet.')
    elif command == "done":
        raise NotImplementedError('Command "done" is not implemented yet.')
    elif command == "search":
        raise NotImplementedError('Command "search" is not implemented yet.')
    elif command == "info":
        raise NotImplementedError('Command "info" is not implemented yet.')
    else:
        raise ValueError(f"Unrecognized command {command}. Run `python {os.path.basename(__file__)} -h` to get help.")
