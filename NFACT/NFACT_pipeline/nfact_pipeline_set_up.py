from NFACT.NFACT_base.utils import error_and_exit
import inspect
import re


def pipeline_args_check(args: dict):
    """
    Function to check that compulsory
    args are given.

    Parameters
    ----------
    args: dict
        command line arguments

    Returns
    -------
    None
    """
    non_complusory = ["target2"]
    for val in args.keys():
        [
            error_and_exit(
                args[val][arg], f"{arg} is not defined. Please define with --{arg}"
            )
            for arg in args[val].keys()
            if arg not in non_complusory
        ]


def get_function_output(function: object) -> dict:
    """
    Function to get the argument and its default



    """
    source_code = inspect.getsource(function)
    pattern = re.compile(
        r'\.add_argument\([^)]*?dest=["\']([a-zA-Z0-9_]+)["\']'
        r"(?:[^)]*?default\s*=\s*([^\s,\)]+))?",
        re.DOTALL,
    )

    matches = pattern.findall(source_code)

    return {dest: (default if default else False) for dest, default in matches}
