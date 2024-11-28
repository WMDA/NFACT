import time
import logging
import sys
import importlib.metadata


class Timer:
    """
    Wrapper around timer
    to calculate how long
    processes take to run
    """

    def __init__(self):
        self._t = time.time()

    def tic(self):
        self._t = time.time()

    def toc(self):
        return f"{time.time()-self._t:.2f}"


def colours():
    """
    Function to print out text in colors

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary object
        dictionary of color strings
    """
    return {
        "reset": "\033[0;0m",
        "red": "\033[1;31m",
        "pink": "\033[1;35m",
        "purple": "\033[38;5;93m",
        "darker_pink": "\033[38;5;129m",
        "plum": "\033[0;35m",
    }


def error_and_exit(bool_statement: bool, error_message: str = None) -> None:
    """
    Function to exit out of script
    with error message if bool statement
    is false.

    Parameters
    ----------
    bool_statement: bool
       statement to evaluate
    error_message: str
        error message to print
        out. Default is None

    Returns
    -------
    None
    """
    if not bool_statement:
        if error_message:
            col = colours()
            nprint(col["red"] + error_message + col["reset"])
        print("Exiting...\n")
        exit(1)


def nprint(message: str) -> None:
    """
    Function to print to terminal
    and attempt to log to pre set up
    log file.

    Parameters
    ----------
    message: str
        string to print and log

    Returns
    -------
    None
    """
    print(message)
    try:
        logging.info(message)
    except Exception:
        return None


def no_args(args: object) -> None:
    """
    Function to print help
    message if no arguments are given.

    Parameters
    ----------
    args: argparse object
        argparse object

    Returns
    -------
    None
    """
    if len(sys.argv) == 1:
        args.print_help(sys.stderr)
        sys.exit(1)


def verbose_help_message(options: object, verbose_message_str: str) -> None:
    """
    Fnction to print out a verbose
    help message.

    Parameters
    ----------
    options: object
        argparse option not parsed
    verbose_message_str: str
        str of additional help message to print

    Returns
    -------
    None
    """
    print(options.format_help())
    print(verbose_message_str)
    print(f"NFACT version: {importlib.metadata.version('NFACT')}")
    exit(0)
