import os
import glob
import re
from NFACT.NFACT_PP.probtrackx_functions import get_probtrack2_arguments
from NFACT.NFACT_base.utils import colours, error_and_exit
from NFACT.NFACT_base.filesystem import make_directory
from NFACT.NFACT_base.setup import check_study_folder_exists


def directory_contains_subjects(study_folder_path: str) -> bool:
    """
    Function to check that study directory contains
    subjects

    Parameters
    ---------
    study_folder_path: str
        study folder path

    Returns
    -------
    bool: boolean
       True if it does else
       False and error messages
    """
    content = [
        direct
        for direct in os.listdir(study_folder_path)
        if os.path.isdir(os.path.join(study_folder_path, direct))
    ]
    if not content:
        col = colours()
        print(f"{col['red']}Study folder is empty{col['reset']}")
        return False
    return True


def check_study_folder_is_dir(study_folder_path: str) -> bool:
    """
    Function to check that study folder is a
    direcotry

    Parameters
    ----------
    study_folder_path: str
        Study folder path

    Returns
    -------
    bool: boolean
       True if is
       else prints error message and
       returns false
    """
    if not os.path.isdir(study_folder_path):
        col = colours()
        print(f"{col['red']}Study folder provided is not a directory{col['reset']}")
        return False

    return True


def check_study_folder(study_folder_path: str) -> bool:
    """
    Check that the study directory exists,
    is a directory and contains subjects

    Parameters
    ----------
    study_folder_path: str
        path to study directory

    Returns
    -------
    bool: boolean
       True if study folder passes
       else prints error message and
       returns false
    """
    if not check_study_folder_exists(
        study_folder_path, "Study folder provided doesn't exist"
    ):
        return False
    if not check_study_folder_is_dir(study_folder_path):
        return False
    if not directory_contains_subjects(study_folder_path):
        return False
    return True


def list_of_subjects_from_directory(study_folder: str) -> list:
    """
    Function to get list of subjects from a directory
    if a list of subjects is not given

    Parameters
    ---------
    study_folder: str
       path to study folder

    Returns
    -------
    list: list object
        list of subjects
    """
    print("Getting list of subjects from directory")
    list_of_subject = glob.glob(os.path.join(study_folder, "*"))
    return [direct for direct in list_of_subject if os.path.isdir(direct)]


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


def check_arguments(arg: dict) -> None:
    """
    Function to check that
    either  hcp_stream given or
    default arguments.

    Parameters
    ----------
    arg: dict
        Command line dictionary

    Returns
    -------
    None
    """
    default_args = ["ref", "seed", "warps", "outdir"]

    for key in default_args:
        if key in default_args[1:] and arg["hcp_stream"]:
            continue
        else:
            error_and_exit(
                arg[key], f"Missing {key} argument. Please specify with --{key}."
            )


def check_surface_arguments(seed: list, roi: list) -> None:
    """
    Function to check that is seeds
    are surfaces then ROIS are provided.

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
    extension = [file.split(".")[-1] for file in seed]
    surface = [file for file in extension if file == "gii"]
    if surface:
        error_and_exit(roi, "Surfaces given as seeds but no ROI. Please provide ROI")
        error_and_exit(
            len(seed) == len(roi), "Number of seeds and number of ROIS must match"
        )
        return True
    return False


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
