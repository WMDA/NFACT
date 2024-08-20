import time


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
    """
    if not bool_statement:
        if error_message:
            col = colours()
            print(col["red"] + error_message + col["reset"])
        print("Exiting...\n")
        exit(1)
