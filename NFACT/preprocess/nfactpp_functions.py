from NFACT.base.utils import error_and_exit
from NFACT.base.imagehandling import check_files_are_imaging_files
from NFACT.base.filesystem import write_to_file, load_json
import os
import re


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
    img_files = [os.path.join(sub, file.lstrip("/")) for file in img_file]
    [
        error_and_exit(
            os.path.exists(path), f"Unable to find {path}. Please check it exists"
        )
        for path in img_files
    ]
    [check_files_are_imaging_files(path) for path in img_files]
    return img_files


def filetree_get_files(filetree: object, sub: str, hemi: str, file: str) -> str:
    """
    Function to get files from filetree.

    Parameters
    ----------
    filetree: FileTree object
        loaded tree
    sub: str
        subject string
    hemi: str
        string of hemishpere
    file: str
        name of file

    Returns
    -------
    file_path:str
    """
    return filetree.update(sub=sub, hemi=hemi).get(file)


def process_filetree_args(arg: dict, sub: str) -> dict:
    """
    Function to process filetree arguments

    Parameteres
    -----------
    arg: dict
        dictionary of command
        line arguments
    sub: str
        string of subject id

    Returns
    -------
    arg: dict
        dictionary of processed
        arguments
    """
    del arg["seed"]
    del arg["rois"]
    arg["seed"] = list(
        set(
            [
                filetree_get_files(arg["file_tree"], sub, hemi, "seed")
                for hemi in ["L", "R"]
            ]
        )
    )
    arg["warps"] = [
        filetree_get_files(arg["file_tree"], sub, "L", "std2diff"),
        filetree_get_files(arg["file_tree"], sub, "L", "diff2std"),
    ]
    arg["bpx_path"] = filetree_get_files(arg["file_tree"], sub, "L", "bedpostX")
    if arg["surface"]:
        arg["rois"] = [
            filetree_get_files(arg["file_tree"], sub, hemi, "medial_wall")
            for hemi in ["L", "R"]
        ]
    return arg


def update_seeds_file(file_path: str) -> None:
    """
    Function to update file extension
    in seeds.txt. Updates surface asc to
    gii.

    Parameters
    ----------
    file_path: str
        string to file path

    Returns
    -------
    None
    """
    try:
        with open(file_path, "r") as file:
            content = file.read()
            update_extensions = content.replace(".asc", ".gii")
        with open(file_path, "w") as file:
            file.write(update_extensions)
    except Exception as e:
        error_and_exit(False, f"Unable to change seeds file due to {e}")


def rename_seed(seeds: list) -> list:
    """
    Function to renmae seed. Either
    will rename it as left_seed or
    right_seed. Or removes unecessary extensions

    Parameters
    ----------
    seed: list
        list of seed names

    Returns
    -------
    seed: list
        list of processed seed names.
    """

    return [
        (
            "left_seed"
            if "L" in (seed_extension := seed.split("."))
            else "right_seed"
            if "R" in seed_extension
            else re.sub(r".gii|.surf", "", os.path.basename(seed))
        )
        for seed in seeds
        if (seed_extension := seed.split("."))
    ]


def get_stop_files_filestree(files_tree: object, subject: str) -> dict:
    """
    Function to get stopping files path
    from

    Parameters
    ----------
    files_tree: object
        FSL.filetree object
    subject: str
        str of subject

    Returns
    -------
    dict: dictionary object
        dict of list wtstop_mask
        and stopping_mask

    """

    return {
        "wtstop_mask": [
            filetree_get_files(files_tree, subject, "L", file)
            for file in files_tree.template_keys()
            if "wtstop" in file
        ],
        "stopping_mask": [
            filetree_get_files(files_tree, subject, "L", file)
            for file in files_tree.template_keys()
            if file.startswith("stop")
        ],
    }


def stoppage(img_file_path: str, file_directory: str, paths_dict: dict) -> list:
    """
    function to write stoppage and wtstop masks
    to file and return the probtrackx commands

    Parameters
    -----------
    img_file_path: str
        path to subject imging file
    file_directory:
        path to nfact_pp/sub/files
        directory
    paths_dict: dict
        dictionary of paths to stoppage and
        wstop masks.

    Returns
    -------
    list: list_oject
        list of additional ptx options
        with --stop and --wtstop
    """

    write_to_file(
        file_directory,
        "stop",
        [
            os.path.join(img_file_path, file + "\n")
            for file in paths_dict["stopping_mask"]
        ],
        text_is_list=True,
    )
    write_to_file(
        file_directory,
        "wtstop",
        [
            os.path.join(img_file_path, file + "\n")
            for file in paths_dict["wtstop_mask"]
        ],
        text_is_list=True,
    )

    return [
        f'--stop={os.path.join(file_directory, "stop")}',
        f'--wtstop={os.path.join(file_directory, "wtstop")}',
    ]


def stop_masks(arg: dict, nfactpp_diretory: str, sub: str, sub_id: str) -> dict:
    """
    Function to process stop masks

    Parameters
    ----------
    arg: dict,
       cmd processes
    nfactpp_diretory: str
        path to nfactpp_directory
    sub: str
        path to sub dirs
    sub_id: str
        subject id

    Returns
    -------
    arg: dict
        dict of cmd lines
    """
    if arg["file_tree"]:
        stop_files = get_stop_files_filestree(arg["file_tree"], sub_id)
    else:
        stop_files = load_json(arg["stop"])
    stop_ptx = stoppage(sub, os.path.join(nfactpp_diretory, "files"), stop_files)
    if arg["ptx_options"]:
        [arg["ptx_options"].append(command) for command in stop_ptx]
    else:
        arg["ptx_options"] = stop_ptx

    return arg
