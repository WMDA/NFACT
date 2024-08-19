import os
from NFACT.utils.utils import (
    error_and_exit,
    read_file_to_list,
    colours,
    load_json,
)
from NFACT.NFACT_decomp.pipes.image_handling import (
    check_files_are_imaging_files,
    get_imaging_details_from_path,
)
from NFACT.NFACT_config.nfact_config_functions import create_combined_algo_dict


def get_subjects(args: dict) -> dict:
    """
    Function to get subjects directly from
    ptx list or from list of subjects.

    Parameters
    ----------
    args: dict
       dictionary of command line
       arguments

    Returns
    -------
    args: dict
       dictionary of command line
       arguments with valid list of subjects
    """
    if args["ptxdir"]:
        if args["list_of_subjects"]:
            col = colours()
            print(
                f'{col["red"]}ptxdir specified. Ignoring list of subjects{col["reset"]}'
            )
        return args
    if args["list_of_subjects"]:
        error_and_exit(
            does_list_of_subjects_exist(args["list_of_subjects"]),
            "List of subjects doesn't exist",
        )
        args["ptxdir"] = return_list_of_subjects_from_file(args["list_of_subjects"])
        return args


def does_list_of_subjects_exist(path_to_list: str) -> bool:
    """
    Function to check if list of subjects
    exists and isn't a directory.

    Parameters
    ----------
    path_to_list: str
        file path to list of subjects

    Returns
    -------
    bool: boolean
       True if list of subjects exists
       else prints error message and
       returns false
    """

    if (not os.path.exists(path_to_list)) or (os.path.isdir(path_to_list)):
        return False
    return True


def check_subject_exist(list_of_subjects: str) -> None:
    """
    Function to check that subjects.
    Exit and errors if they don't

    Parameters
    ----------
    list_of_subjects: str
        list of subjects

    Returns
    -------
    None
    """
    [
        error_and_exit(
            os.path.exists(path),
            f"{path} does not exist. Please check provided subjects",
        )
        for path in list_of_subjects
    ]


def return_list_of_subjects_from_file(path_to_list: str) -> list:
    """
    Function to return list of subjects from a file

    Parameters
    ----------
    path_to_list: str
        path to subject directory

    Returns
    -------
    list_of_subjects: list
        list of subjects
    """
    # First check that list of subjects is a txt file.
    try:
        if path_to_list.split(".")[1] != "txt":
            error_and_exit(
                False,
                "List of subjects is not a text file. Please specify a list of subject.",
            )
    # Hacky way to allow sub list not to have an extension
    except IndexError:
        pass
    try:
        list_of_subjects = read_file_to_list(path_to_list)
    except Exception as e:
        error_and_exit(False, f"Unable to open subject list due to: {e}")
    return list_of_subjects


def process_seeds(seeds: str) -> list:
    """
    Function to read in seed file

    Parameters
    ----------
    seeds: str
        str to file with
        seeds in them.

    Returns
    -------
    list_of_seeds: list
        list of seed files
    """
    try:
        list_of_seeds = read_file_to_list(seeds)
    except Exception as e:
        error_and_exit(False, f"Unable to read seeds text file due to {e}")

    [check_files_are_imaging_files(seed) for seed in list_of_seeds]
    return list_of_seeds


def imaging_type(path: str) -> str:
    """
    Function to return imaging
    type based on extension.

    Parameters
    ----------
    path: str
        path to str

    Return
    ------
    str: string
        str of nifit or gifti
    """
    file_extensions = get_imaging_details_from_path(path)["file_extensions"]
    if ".nii" in file_extensions:
        return "nifti"
    if ".gii" in file_extensions:
        return "gifti"


def seed_type(seeds: list) -> str:
    """
    Function to get seed imaging
    type from paths.

    Parameter
    ---------
    seeds: list
        list of seed type

    Returns
    -------
    str: string
        str of nifti or gifti.
    """
    seed_imaging_file = [imaging_type(path) for path in seeds]
    error_and_exit(
        all(item == seed_imaging_file[0] for item in seed_imaging_file),
        "Seeds are not of the same type.",
    )
    return seed_imaging_file[0]


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
