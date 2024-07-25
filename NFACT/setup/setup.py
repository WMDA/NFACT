import os
from NFACT.utils.utils import (
    error_and_exit,
    read_file_to_list,
    colours,
    make_directory,
    load_json,
)
from NFACT.pipes.image_handling import check_files_are_imaging_files
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


def create_folder_set_up(directory: str) -> None:
    """
    Function to create NFACT directory set up

    Parameters
    ----------
    directory: str
        path to directory to save output
        in.

    Returns
    -------
    None
    """
    error_and_exit(
        os.path.exists(directory),
        "Output directory does not exist. Please provide actual directory",
    )
    col = colours()
    print(f"{col['purple']}nfact folder is in {directory}{col['reset']}")
    nfact_directory = os.path.join(directory, "nfact")

    sub_folders = [
        "group_averages",
        "ICA",
        "NFM",
        "GLM",
        "ICA/dual_reg",
        "NFM/dual_reg",
        "ICA/normalised",
        "NFM/normalised",
        "ICA/dual_reg/G",
        "ICA/dual_reg/W",
        "NFM/dual_reg/G",
        "NFM/dual_reg/W",
    ]

    does_exist = os.path.exists(nfact_directory)

    if does_exist:
        sub_folders = which_nfact_folders_exist(nfact_directory, sub_folders)

        if len(sub_folders) == 0:
            return None

    if not does_exist:
        make_directory(nfact_directory)

    [make_directory(os.path.join(nfact_directory, sub)) for sub in sub_folders]


def which_nfact_folders_exist(nfact_directory: str, sub_folders: list) -> list:
    """
    Function to check which nfact sub folders
    don't exist

    Parameters
    ----------
    nfact_directory: str
        path to nfact directory
    sub_folders: list
        list of sub folders

    Returns
    -------
    sub_folders_that_dont_exist: list
        list of sub folders that don't exist
    """

    sub_folders_that_dont_exist = []
    [
        sub_folders_that_dont_exist.append(sub)
        for sub in sub_folders
        if not os.path.exists(os.path.join(nfact_directory, sub))
    ]
    return sub_folders_that_dont_exist


def list_of_fdt_mat(list_ptx_folder: list) -> list:
    """
    Function to get list of matricies

    Parameters
    ----------
    list_ptx_folder: list
        list of ptx folders

    Returns
    -------
    list: list object
       list of subjects fdt_matrix2.dot
       paths
    """
    return [
        os.path.join(sub_folder, "fdt_matrix2.dot") for sub_folder in list_ptx_folder
    ]


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
