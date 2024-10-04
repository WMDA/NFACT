from .probtrackx_functions import get_probtrack2_arguments
from NFACT.base.utils import colours, error_and_exit
from NFACT.base.filesystem import make_directory
import os
import re
from file_tree import FileTree


def check_fsl_is_installed():
    """
    Function to check that FSL is
    installed. Checks for FSLDIR
    in enviormental variables

    Parameters
    ----------
    None

    Returns
    -------
    bool: boolean
        True if installed
        else False with error message.
    """
    fsl_loaded = os.getenv("FSLDIR")
    if not fsl_loaded:
        return False
    return True


def check_seeds_surfaces(seed: list) -> bool:
    """
    Function to check that is seeds
    are surfaces then ROIS are provided.

    Parameters
    ----------
    seed: list
        list of seeds

    Returns
    -------
    None
    """
    surface = [file for file in seed if ".gii" in file]
    if surface:
        return True
    return False


def check_roi_seed_len(seed: list, roi: list):
    """
    Function to check that the same
    amount of seed(s) and roi(s)
    are given.
    Parameters
    ----------
    seed: list
        list of seeds
    roi: list
        list of ROIS
    Returns
    -------
    None
    """
    error_and_exit(roi, "Surfaces given as seeds but no ROI. Please provide ROI")
    error_and_exit(
        len(seed) == len(roi), "Number of seeds and number of ROIS must match"
    )


def check_ptx_options_are_valid(ptx_options: list):
    """
    Function to check that ptx options
    valid options. Errors out if
    any are not valid options

    Parameters
    ----------
    ptx_options: list
       list of user defined options

    Returns
    -------
    None
    """

    check_out = get_probtrack2_arguments()
    probtrack_args = re.findall(r"-.*?\t", check_out)
    stripped_args = [arg.rstrip("\t") for arg in probtrack_args]
    probtrack_args = sum([arg.split(",") for arg in stripped_args], [])
    [
        error_and_exit(False, f"{arg} is not a probtrackx2 option")
        for arg in ptx_options
        if arg not in probtrack_args
    ]


def nfact_pp_folder_setup(nfactpp_diretory: str) -> None:
    """
    Function to create nfact pp folder set up

    Parameters
    ----------
    nfactpp_diretory: str
        path to directory

    Returns
    -------
    None
    """
    col = colours()
    print(
        f"{col['pink']}nfact pre-processing folder is in {nfactpp_diretory}{col['reset']}"
    )

    make_directory(nfactpp_diretory)
    sub_folders = ["logs", "files"]
    [make_directory(os.path.join(nfactpp_diretory, sub)) for sub in sub_folders]


def load_file_tree(tree_name):
    try:
        tree = FileTree.read(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "filetrees", tree_name
            )
        )
        return tree
    except Exception as e:
        error_and_exit(False, f"Unable to load tree file, due to {e}")
