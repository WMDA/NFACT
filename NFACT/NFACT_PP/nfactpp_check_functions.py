import os
import glob
import pathlib
import re
from NFACT.NFACT_PP.nfactpp_utils_functions import colours, read_file_to_list, error_and_exit
from NFACT.NFACT_PP.nfactpp_probtrackx_functions import get_probtrack2_arguments


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


def check_study_folder_exists(study_folder_path: str) -> bool:
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
        print(f"{col['red']}Study folder provided doesn't exist{col['reset']}")
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
    if not check_study_folder_exists(study_folder_path):
        return False
    if not check_study_folder_is_dir(study_folder_path):
        return False
    if not directory_contains_subjects(study_folder_path):
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
            col = colours()
            print(f"""{col['red']}List of subjects is not ascii file. 
                  Please specify a list of subject or remove flag.{col['reset']}""")

            return None
    # Hacky way to allow sub list not to have an extension
    except IndexError:
        pass

    try:
        list_of_subjects = read_file_to_list(path_to_list)
    except Exception as e:
        col = colours()
        print(f"{col['red']}Unable to open subject list due to: {e}{col['reset']}")

    return list_of_subjects


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


def get_file(img_file: list, sub: str) -> list:
    """
    Function to get an imaging file
    type and returns it. Checks that file
    is correct file type and exists.

    Parameters
    ----------
    img_file: list
        a list of imaging files
    sub: str
       path to subjects directory.

    Returns
    -------
    img_files: list
        list of imging files

    """
    img_files = [os.path.join(sub, file) for file in img_file]
    [
        error_and_exit(
            os.path.exists(path), f"Unable to find {path}. Please check it exists"
        )
        for path in img_files
    ]
    [check_files_are_imaging_files(path) for path in img_files]
    return img_files


def check_files_are_imaging_files(path: str) -> bool:
    """
    Function to check that imaging files
    are actually imaging files.

    Parameters
    ----------

    Returns
    -------
    None
    """
    accepted_extenions = [".gii", ".nii"]
    file_extensions = pathlib.Path(path).suffixes
    file = os.path.basename(path)
    sub = os.path.basename(os.path.dirname(path))
    error_and_exit(
        [file for file in file_extensions if file in accepted_extenions],
        f"{file} for {sub} is an incorrect file type (not gii or nii)",
    )


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
    keys = ["seed", "warps"]
    default_arguments = {key: arg[key] for key in keys}
    if not arg["hcp_stream"]:
        for key, value in default_arguments.items():
            error_and_exit(
                value, f"Missing {key} argument. Please specify or use --hcp_stream"
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
