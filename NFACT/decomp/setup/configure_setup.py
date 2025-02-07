from NFACT.base.utils import error_and_exit
from NFACT.base.filesystem import load_json
from NFACT.config.nfact_config_functions import create_combined_algo_dict


def load_config_file(path: str, algo: str) -> dict:
    """
    Function to read in a config file
    and return only the appropriate

    Parameters
    ----------
    path: str
       path to config file
    algo: str
       which algo is being ran

    Returns
    -------
    dict: dictionary object
        dictionary of arguments

    """
    config = load_json(path)
    return config[algo]


def check_config_file(config_file: dict, algo: str) -> None:
    """
    Function to check that parameters
    in the config file match parameters of
    a given function.

    Parameters
    ----------
    config_file: dict
       config file
    algo: str
       which algo is being ran

    Returns
    -------
    None

    """
    default_values = create_combined_algo_dict()[algo].keys()
    [
        error_and_exit(
            False,
            f"{val} is not a {algo} parameter. Please check the sckit learn documentation for parameters",
        )
        for val in config_file.keys()
        if val not in default_values
    ]
