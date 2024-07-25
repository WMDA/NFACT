from NFACT.utils.utils import make_directory, error_and_exit, colours
import os
import shutil


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


def get_group_average_files(file_directory: str, nfact_directory: str) -> None:
    """
    Function to move lookup_tractspace_fdt_matrix2 and
    coords_for_fdt_matrix2 of a subject to a the group
    average folder.

    Parameters
    ----------
    file_directory: str
        file directory of a omatrix2 file
    nfact_direcotry: str
        string of path to group_averages nfact
        directory

    Returns
    -------
    None
    """
    lookup_space = os.path.join(file_directory, "lookup_tractspace_fdt_matrix2.nii.gz")
    coords_for_fdt_matrix2 = os.path.join(file_directory, "coords_for_fdt_matrix2")
    [
        error_and_exit(
            os.path.exists(file), f"{file} does not exist. Please check pre-processing"
        )
        for file in [lookup_space, coords_for_fdt_matrix2]
    ]
    shutil.copyfile(
        lookup_space,
        os.path.join(nfact_directory, "lookup_tractspace_fdt_matrix2.nii.gz"),
    )
    shutil.copyfile(
        lookup_space, os.path.join(nfact_directory, "coords_for_fdt_matrix2")
    )
