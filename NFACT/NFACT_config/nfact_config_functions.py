import inspect
from sklearn.decomposition import FastICA, NMF
import json
import os
import argparse
from NFACT.NFACT_decomp.utils.utils import colours


def nfact_config_args():
    """
    Function to define cmd arguments

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary
        dictionary of cmd arguments
    """
    args = argparse.ArgumentParser(
        prog="nfact_config",
        description=print(nfact_config_spalsh()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    args.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        default=os.getcwd(),
        help="Where to save config file",
    )

    return vars(args.parse_args())


def nfact_config_spalsh() -> str:
    """
    Function to return NFACT config
    splash

    Parameters
    ----------
    None

    Returns
    -------
    str: splash
    """
    col = colours()
    return f"""
{col['pink']} 
 _   _______ ___  _____ _____                    __ _       
| \ | |  ___/ _ \/  __ \_   _|                  / _(_)      
|  \| | |_ / /_\ \ /  \/ | |     ___ ___  _ __ | |_ _  __ _ 
| . ` |  _||  _  | |     | |    / __/ _ \| '_ \|  _| |/ _` |
| |\  | |  | | | | \__/\ | |   | (_| (_) | | | | | | | (_| |
\_| \_|_|  \_| |_/\____/ \_/    \___\___/|_| |_|_| |_|\__, |
                                                       __/ |
                                                      |___/ 
{col['reset']} 
"""


def get_arguments(function: object) -> dict:
    """
    Function to get default arguments
    and put them into a dictionary object

    Parameters
    ----------
    function: object
       function to get arguments from

    Returns
    -------
    dict: dictionary object
        dict of functions
    """
    signature = inspect.signature(function)
    return dict(
        zip(
            [param.name for param in signature.parameters.values()],
            [
                param.default
                for param in signature.parameters.values()
                if param.default is not inspect.Parameter.empty
            ],
        )
    )


def create_combined_algo_dict():
    """
    Function to create a combined dictionary
    for nmf and ICA function arguments.

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary object
        dict of ICA and NMF
        arguments
    """
    dictionary_to_save = {"ica": get_arguments(FastICA), "nmf": get_arguments(NMF)}
    del dictionary_to_save["nmf"]["n_components"]
    del dictionary_to_save["ica"]["n_components"]
    return dictionary_to_save


def save_to_json(path: str, dictionary_to_save: dict):
    """
    Function to save nfact config file
    to disk as a json.

    Parameters
    ----------
    path: str
       string of path of where to save the config
       file
    dictionary_to_save: dict
        dictionary of arguements

    Returns
    -------
    None
    """

    config_file = json.dumps(dictionary_to_save)
    with open(os.path.join(path, "nfact_config.config"), "w") as json_file:
        json_file.write(config_file)
