from .probtrackx_functions import get_probtrack2_arguments
from NFACT.base.utils import colours, error_and_exit
from NFACT.base.filesystem import make_directory
from NFACT.base.imagehandling import check_files_are_imaging_files
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


def check_roi_seed_len(seed: list, roi: list):
    """
    Function to check that the same
    amount of seed(s) and roi
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
    error_and_exit(
        roi,
        "Surfaces given as seeds but no medial wall. Please provide medial wall",
    )
    error_and_exit(
        len(seed) == len(roi),
        "Number of seeds and number of medial wall must match",
    )


def clean_ptx_options(ptx_options: list) -> list:
    """
    Function to clean ptx options
    from a file.

    Parameters
    ----------
    ptx_options: list
       list of user defined options

    Returns
    -------
    ptx_args: list
        list of ptx args from file
    """
    ptx_args = []
    for ptx in ptx_options:
        try:
            ptx_args.append(re.findall(r"(-\w+|--\w+)", ptx)[0])
        except IndexError:
            continue
    return ptx_args


def check_ptx_options_are_valid(ptx_options: list) -> None:
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
    ptx_options_clean = clean_ptx_options(ptx_options)

    [
        error_and_exit(False, f"{arg} is not a probtrackx2 option")
        for arg in ptx_options_clean
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
    print(f"{col['pink']}nfact_PP folder:{col['reset']} {nfactpp_diretory}")
    make_directory(nfactpp_diretory)
    sub_folders = ["logs", "files"]
    [make_directory(os.path.join(nfactpp_diretory, sub)) for sub in sub_folders]


def load_file_tree(tree_name: str) -> object:
    """
    Function to load tree object

    Parameters
    ----------
    tree_name: str
        str of tree name to load

    Returns
    -------
    tree: FileTree object
        filetree object
    """
    try:
        tree = FileTree.read(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "filetree", tree_name
            )
        )
        return tree
    except Exception as e:
        error_and_exit(False, f"Unable to load tree file, due to {e}")


def check_provided_img(image_to_check: str, error_messgae: str) -> None:
    """
    Wrapper around function to
    check exclusion masks is a file
    and exists.
    """
    error_and_exit(os.path.isfile(image_to_check), error_messgae)
    check_files_are_imaging_files(image_to_check)
