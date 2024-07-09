import time


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Helper class for timing
class Timer:
    def __init__(self):
        """
        Matlab-style timer class
        t = timer()
        t.tic()
        .... do stuff
        t.toc()
        """
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
    }


def error_and_exit(bool_statement: bool, error_message=None):
    """
    Function to exit out of script
    with error message if bool statement
    is false
    """
    if not bool_statement:
        if error_message:
            col = colours()
            print(col["red"] + error_message + col["reset"])
        print("Exiting...\n")
        exit(1)
