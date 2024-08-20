import os
from NFACT.NFACT_base.utils import error_and_exit
from NFACT.NFACT_base.filesystem import read_file_to_list


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
        return args
    if args["list_of_subjects"]:
        error_and_exit(
            does_list_of_subjects_exist(args["list_of_subjects"]),
            "List of subjects doesn't exist",
        )
        args["ptxdir"] = return_list_of_subjects_from_file(args["list_of_subjects"])
        return args
