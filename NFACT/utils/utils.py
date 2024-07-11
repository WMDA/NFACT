import time
import signal


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


class Signit_handler:
    """
    A signit handler class. Will kill. Exits
    programme safely.
    """

    def __init__(
        self,
    ) -> None:
        self.register_handler()
        self.suppress_messages = False

    def register_handler(self) -> None:
        """
        Method to registers the SIGINT handler.
        """
        signal.signal(signal.SIGINT, self.handle_sigint)

    def handle_sigint(self, sig, frame) -> None:
        """
        Method that handles the SIGINT signal (Ctrl+C)

        Parameters
        -----------
        sig: The signal number
        frame: The current stack frame
        """
        if not self.suppress_messages:
            col = colours()
            print(
                f"\n{col['darker_pink']}Recieved kill signal (Ctrl+C). Terminating..."
            )
            print(f"Exiting...{col['reset']}\n")
        exit(0)

    @property
    def get_suppress_messages(self):
        """
        Getter method for suppress_messages
        """
        return self.suppress_messages

    @get_suppress_messages.setter
    def set_suppress_messages(self, value: bool) -> None:
        """
        Setter for suppress_messages
        """
        self.suppress_messages = value


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
