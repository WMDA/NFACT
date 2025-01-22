from .utils import error_and_exit
from .filesystem import read_file_to_list, make_directory
from .imagehandling import check_files_are_imaging_files
import os


def process_input_imgs(list_of_img: str) -> list:
    """
    Function to read in seed file

    Parameters
    ----------
    img_path: str
        str to file with
        img_path in them.

    Returns
    -------
    list_of_img: list
        list of seed files
    """
    try:
        list_of_img = read_file_to_list(list_of_img)
    except Exception as e:
        error_and_exit(False, f"Unable to read text file due to {e}")
    [check_files_are_imaging_files(img_file) for img_file in list_of_img]
    return list_of_img


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
    accepted_types = ["txt", "sublist"]
    try:
        file_name = os.path.basename(path_to_list)
        if file_name.split(".")[1] not in accepted_types:
            error_and_exit(
                False,
                "List of subjects is not a text file. Please specify a list of subject.",
            )
    # Hacky way to allow sub list not to have an extension
    except IndexError:
        pass
    try:
        list_of_subjects = read_file_to_list(path_to_list)
        # Remove empty lines
        list_of_subjects = [sub for sub in list_of_subjects if sub.strip()]
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


def check_arguments(arg: dict, comp_args: list) -> None:
    """
    Function to check complusory arguments
    and exits if not given

    Parameters
    ----------
    arg: dict
        Command line dictionary
    comp_args: list
         list of complusory arguments

    Returns
    -------
    None
    """

    for key in comp_args:
        error_and_exit(
            arg[key], f"Missing {key} argument. Please specify with --{key}."
        )


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


def check_medial_wall(args) -> dict:
    """
    Function to check medial wall and
    process if given.

    Parameters
    ----------
    arg: dict
        cmd arguements

    Returns
    -------
    arg: dict
        cmd arguments if processed
        medial wall
    """

    if args["surface"] and args["medial_wall"]:
        args["medial_wall"] = process_input_imgs(args["medial_wall"])
        return args
    if args["surface"] and not args["medial_wall"]:
        error_and_exit(False, "Seeds are surface files but no medial wall given.")


def process_dim(dim: str) -> str:
    """
    Function to process dimensions from
    command line input.

    Parameters
    ----------
    dim: str
        number of dimensions
    Returns
    -------
    dim: int/float
        number of dimensions as
        float or int
    """
    dim = str(dim)
    if ".0" in dim:
        dim = float(dim)
    try:
        dim = int(dim)
    except Exception:
        error_and_exit(
            False,
            f"Dimmensions must be a interger value. {dim} is not a interger type",
        )

    return dim


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
    None
    """
    fsl_loaded = os.getenv("FSLDIR")
    error_and_exit(
        fsl_loaded,
        "FSLDIR not in path. Check FSL is installed or has been loaded correctly",
    )
