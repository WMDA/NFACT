from .utils import error_and_exit, colours
from .filesystem import read_file_to_list, make_directory
from .imagehandling import (
    check_files_are_imaging_files,
    get_imaging_details_from_path,
)
import os


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


def check_study_folder_exists(study_folder_path: str, error_messgae: str) -> bool:
    """
    Function to check that study folder exists

    Parameters
    ----------
    study_folder_path: str
        Study folder path

    Returns
    -------
    bool: boolean
       True if does exist
       else prints error message and
       returns false
    """
    if not os.path.exists(study_folder_path):
        col = colours()
        print(f"{col['red']}{error_messgae}{col['reset']}")
        return False
    return True


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
        file_name = os.path.basename(path_to_list)
        if file_name.split(".")[1] != "txt":
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


def check_algo(algo: str) -> str:
    """
    Function to check that decomposition
    is implemented in NFACT.

    Parameters
    ----------
    algo: str
       string of decomp method.

    Returns
    -------
    algo: str
       returns lower case
       of str
    """
    error_and_exit(
        algo, "--algo not given. Please specify either ICA and NMF (case insensitive)"
    )
    implemented_decomp_methods = ["nmf", "ica"]
    if algo.lower() not in implemented_decomp_methods:
        error_and_exit(
            False,
            f"{algo} is not implemented in NFACT. NFACT currently implements ICA and NMF (case insensitive). Please specify with --algo",
        )
    return algo.lower()


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

        [
            error_and_exit(
                os.path.isdir(item),
                "ptxdir argument is not a list of subject directories.",
            )
            for item in args["ptxdir"]
        ]
        return args
    if args["list_of_subjects"]:
        error_and_exit(
            does_list_of_subjects_exist(args["list_of_subjects"]),
            "List of subjects doesn't exist",
        )
        args["ptxdir"] = return_list_of_subjects_from_file(args["list_of_subjects"])
        return args


def which_folders_dont_exist(nfact_directory: str, sub_folders: list) -> list:
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


def creat_subfolder_setup(directory: str, sub_folders: list) -> None:
    """
    Function to create folder and sub folders
    used for nfact. Checks if they exist already
    and if not it creates them.

    Parameters
    ----------
    directory: str
        string to path to check if directory
        already exists

    sub_folders: list
        list of sub folders to create

    Returns
    -------
    None
    """
    does_exist = os.path.exists(directory)

    if does_exist:
        sub_folders = which_folders_dont_exist(directory, sub_folders)

        if len(sub_folders) == 0:
            return None

    if not does_exist:
        make_directory(directory)

    [make_directory(os.path.join(directory, sub)) for sub in sub_folders]
