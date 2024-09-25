from NFACT.NFACT_base.setup import check_study_folder_exists, creat_subfolder_setup
from NFACT.NFACT_base.utils import error_and_exit

import os


def check_compulsory_arguments(args: dict) -> None:
    """
    Function to check that complusory arguments
    are provided.

    Parameters
    ----------
    args: dict
        A dictionary of args

    Returns
    -------
    None
    """
    error_and_exit(
        (False if not args["ptxdir"] and not args["list_of_subjects"] else True),
        "No subjects provided. Please provide a list of subjects with either --ptxdir or --list_of_subjects",
    )
    error_and_exit(
        args["seeds"], "No seeds provided. Please use --seeds to provide seeds"
    )


def check_nfact_decomp_directory(nfact_directory: str, algo: str) -> None:
    """
    Function to check the NFACT directory has the
    components and group averages needed.

    Parameters
    ----------
    nfact_directory: str
        string of path to nfact directory
    algo: str
        string of algo to perform regression on.

    Returns
    -------
    None
    """
    error_and_exit(
        check_study_folder_exists(
            nfact_directory,
            "NFACT decomposition directory does not exist. Check the given path and that group level decompoisition has been ran.",
        )
    )

    error_and_exit(
        (
            False
            if not os.path.exists(
                os.path.join(nfact_directory, "components", algo.upper(), "decomp")
            )
            or not os.listdir(
                os.path.join(nfact_directory, "components", algo.upper(), "decomp")
            )
            else True
        ),
        "No components found. Please check that decomposition has been ran.",
    )

    error_and_exit(
        (
            False
            if not os.path.exists(os.path.join(nfact_directory, "group_averages"))
            or not os.listdir(os.path.join(nfact_directory, "group_averages"))
            else True
        ),
        f"No group averages found. Please make sure that coords and lookup tractspace are in {os.path.join(nfact_directory, 'group_averages')}",
    )


def create_nfact_dr_folder_set_up(nfact_path: str) -> None:
    """
    Function to create nfact dr folder set up

    Parameters
    ----------
    nfact_pat: str
        string to nfact directory

    Returns
    -------
    None
    """
    subfolders = ["logs", "ICA", "NMF", "ICA/normalised", "NMF/normalised"]
    nfactdr_directory = os.path.join(nfact_path, "nfact_dr")
    creat_subfolder_setup(nfactdr_directory, subfolders)
