from NFACT.NFACT_base.utils import error_and_exit
import os


def check_for_duplicates(
    paths_dict: dict, match_files: list, matches_folders: list, search_dir
) -> None:
    """
    Function to check if found a duplicate

    Parameters
    ----------
    paths_dict: dict
        dictionary of found paths
    match_files: list
        a list of found files
    matches_folders: list
        a list of found folders

    Returns
    -------
    None
    """
    [
        error_and_exit(
            f"Found duplicate {item} in {search_dir}. Please make sure there are no duplicate files in folder"
        )
        for item in (match_files + matches_folders)
        if item in paths_dict.keys()
    ]


def find_file(search_dir: str, files_to_find: list, dir_to_find: str) -> dict:
    """
    Function to find files in a given folder.

    Parameters
    ----------
    search_dir: str
        path to directory to search
    files_to_find: list
        list of target file
    dir_to_find: str
        directory to find

    Returns
    -------
    paths: dict
        dictionary of file paths
        to files
    """

    paths = {}
    for root, dirs, files in os.walk(search_dir):
        matched_files = set(files_to_find).intersection(files)
        matched_folds = [direct for direct in dirs if dir_to_find in direct]
        check_for_duplicates(
            paths, list(matched_files), list(matched_folds), search_dir
        )
        paths.update(
            {
                sub_dir: os.path.join(root, sub_dir)
                for sub_dir in matched_folds
                if sub_dir in dir_to_find
            }
        )
        paths.update({file: os.path.join(root, file) for file in matched_files})
    return paths


def get_files(search_dir: str, arg: dict):
    files_needed = arg["seed"] + arg["warps"]
    if arg["surface"]:
        files_needed = files_needed + arg["rois"]
    paths = find_file(search_dir, files_needed, arg["bpx_path"])

    path_to_files = {
        "seed": [paths[seed] for seed in arg["seed"]],
        "warps": [paths[warp] for warp in arg["warps"]],
    }
    path_to_files.update({key: paths[key] for key in paths if key.endswith("bedpostX")})

    if arg["surface"]:
        path_to_files.update({"rois": [paths[roi] for roi in arg["rois"]]})

    return path_to_files
