import inspect
from sklearn.decomposition import FastICA, NMF
import json
import os


def nfact_config_args():
    return


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
    for NFM and ICA function arguments.

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary object
        dict of ICA and NMF
        arguments
    """
    return {"ica": get_arguments(FastICA), "nfm": get_arguments(NMF)}


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
    config_file = json.dumps(dictionary_to_save, indent=4)
    with open("nfact_config.config") as json_file:
        json_file.write(os.path.join(path, config_file))


print(json.dumps({"ica": get_arguments(FastICA), "nfm": get_arguments(NMF)}, indent=4))

#
#
## Dump the dictionary to a JSON object
# args_json = json.dumps(args_dict, indent=4)
#
# print(args_json)

#
#
# beta_loss_pattern = re.compile(r'.*\s*:\s*{\s*([^}]*)\s*}')
# match = beta_loss_pattern.findall(signature)
# print(match)
