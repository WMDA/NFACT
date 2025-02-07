from NFACT.base.setup import creat_subfolder_setup
from NFACT.base.utils import error_and_exit

import os


def check_nfact_decomp_directory(comp_directory: str, group_average_dir: str) -> None:
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
        (
            False
            if not os.path.exists(comp_directory) or not os.listdir(comp_directory)
            else True
        ),
        f"No components found in {comp_directory}. Please check that components exist",
    )

    error_and_exit(
        (
            False
            if not os.path.exists(group_average_dir)
            or not os.listdir(group_average_dir)
            else True
        ),
        f"No group averages found. Please make sure that coords and lookup tractspace are in {group_average_dir}",
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
    error_string = "Please provide a directory with --outdir"
    error_and_exit(nfact_path, f"No output direcotry given. {error_string}")
    error_and_exit(
        os.path.exists(nfact_path), f"Output directory does not exist. {error_string}"
    )
    subfolders = ["logs", "ICA", "NMF", "ICA/normalised", "NMF/normalised"]
    nfactdr_directory = os.path.join(nfact_path, "nfact_dr")
    creat_subfolder_setup(nfactdr_directory, subfolders)
