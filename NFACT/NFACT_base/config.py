from NFACT.NFACT_PP.nfactpp_args import nfact_pp_args
from NFACT_decomp.setup.args import nfact_decomp_args
from NFACT.NFACT_DR.nfact_dr_args import nfactdr_args
import inspect
import re


def get_function_output(function: object) -> dict:
    """
    Function to get the argument and its default
    values in dictionary form. If no defaults
    present then it will default to false.

    Parameters
    ----------
    function: object
        function object (nfact arg) to
        read argument from

    Returns
    -------
    dict: dictionary object
        dict of arg and default.
    """

    source_code = inspect.getsource(function)
    pattern = re.compile(
        r'\.add_argument\([^)]*?dest=["\']([a-zA-Z0-9_]+)["\']'
        r"(?:[^)]*?default\s*=\s*([^\s,\)]+))?",
        re.DOTALL,
    )

    matches = pattern.findall(source_code)

    return {dest: (default if default else False) for dest, default in matches}


def get_nfact_arguments() -> dict:
    """
    Function to get nfact_pp, nfact_decomp
    and nfact_dr args into a dictionary.

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary object
        dict of module iwth arg, default pair.
    """
    return {
        "nfact_pp": get_function_output(nfact_pp_args),
        "nfact_decomp": get_function_output(nfact_decomp_args),
        "nfact_dr": get_function_output(nfactdr_args),
    }
