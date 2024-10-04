from NFACT.base.utils import colours, error_and_exit, no_args
from NFACT.base.filesystem import write_to_file
import inspect
from sklearn.decomposition import FastICA, NMF
import json
import os
import argparse
import glob


def nfact_config_args() -> dict:
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
        "-C",
        "--config",
        dest="config",
        action="store_true",
        help="Creates a config file for NFACT pipeline",
    )
    args.add_argument(
        "-D",
        "--decomp_only",
        dest="decomp_only",
        action="store_true",
        help="Creates a config file for sckitlearn function hyperparameters",
    )
    args.add_argument(
        "-s",
        "--subject_list",
        dest="subject_list",
        default=False,
        help="Creates a subject list from a given directory",
    )

    args.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        default=os.getcwd(),
        help="Where to save config file",
    )
    no_args(args)

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


def create_combined_algo_dict() -> dict:
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


def save_to_json(path: str, dictionary_to_save: dict, file_name: str) -> None:
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
    with open(os.path.join(path, f"{file_name}.config"), "w") as json_file:
        json_file.write(config_file)


def check_arguments(args):
    arg_type = ["decomp_only", "config", "subject_list"]
    matching = [arg for arg in args.keys() if arg in arg_type and args[arg]]
    if len(matching) > 1:
        error_and_exit(
            False,
            f"""Multiple arguments were given {matching}. 
Please specify either --decomp --config or --subject_list only""",
        )


def check_study_folder(study_folder_path: str) -> None:
    """
    Function to check that study directory
    is a directory with subjects in it it.

    Parameters
    ----------
    study_folder_path: str
        path to study directory

    Returns
    -------
    None
    """
    error_and_exit(
        os.path.exists(study_folder_path), "Study folder provided doesn't exist"
    )
    error_and_exit(
        os.path.isdir(study_folder_path), "Study directory is not a directory"
    )
    error_and_exit(
        [
            dirs
            for dirs in os.listdir(study_folder_path)
            if os.path.isdir(os.path.join(study_folder_path, dirs))
        ],
        "Study directory is empty",
    )


def list_of_subjects_from_directory(study_folder_path: str) -> list:
    """
    Function to get list of subjects from a directory
    if a list of subjects is not given

    Parameters
    ---------
    study_folder_path: str
       path to study folder

    Returns
    -------
    list: list object
        list of subjects
    """
    list_of_subject = glob.glob(os.path.join(study_folder_path, "*"))
    return [f"{direct}\n" for direct in list_of_subject if os.path.isdir(direct)]


def filter_sublist(sub_list: str) -> list:
    """
    Fucntion to filter sub list to
    remove directories that are unlikely to
    be

    Parameters
    ----------
    sub_list: list
        list of subjects

    Returns
    -------
    list: list object
        filtered list of subjects
    """

    remove_dir = ["analysis", "code", "sourcedata", "derivatives", "."]

    return [
        dirs
        for dirs in sub_list
        if not any(os.path.basename(dirs).lower().startswith(rem) for rem in remove_dir)
    ]


def create_subject_list(study_folder_path: str, ouput_dir: str) -> None:
    """
    Function to create subjects
    study list

    Parameters
    ---------
    study_folder_path: str
        path to study folder
    ouput_dir: str
        path to output directory

    Returns
    -------
    None
    """
    check_study_folder(study_folder_path)
    sub_list = list_of_subjects_from_directory(study_folder_path)
    sub_list = filter_sublist(sub_list)
    write_to_file(ouput_dir, "nfact_config_sublist", sub_list, text_is_list=True)
    return None
