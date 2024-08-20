import os
import glob
from NFACT.NFACT_base.utils import error_and_exit


def hcp_get_seeds(sub: str) -> list:
    """
    Function to get HCP stream seeds

    Parameters
    ----------
    sub: str
        string of subject

    Returns
    -------
    seeds: list
       list of seeds
    """
    seeds = glob.glob(
        os.path.join(sub, f"MNINonLinear/fsaverage_LR32k/*.white.32k_fs_LR.surf.gii")
    )
    subject = os.path.basename(sub)
    error_and_exit(seeds, f"Cannot find seed files for {subject}")
    return seeds


def hcp_get_rois(sub: str) -> list:
    """
    Function to get HCP stream ROIS

    Parameters
    ----------
    sub: str
        string of subject

    Returns
    -------
    rois: list
       list of rois
    """
    rois = glob.glob(
        os.path.join(
            sub, f"MNINonLinear/fsaverage_LR32k/*.atlasroi.32k_fs_LR.shape.gii"
        )
    )
    subject = os.path.basename(sub)
    error_and_exit(rois, f"Cannot find seed files for {subject}")
    return rois


def hcp_reorder_seeds_rois(seeds: list, rois: list) -> dict:
    """
    Function to return seeds and rois
    in same order.

    Parameters
    ----------
    seeds: list
        a list of seeds
    rois: list
        a list of rois

    Returns
    -------
    dict: dict
        dictionary of left/right
        hemisphere seed and ROI

    """
    left_seed = [seed for seed in seeds if "L.white" in seed][0]
    right_seed = [seed for seed in seeds if "R.white" in seed][0]
    left_rois = [roi for roi in rois if "L.atlasroi" in roi][0]
    right_rois = [roi for roi in rois if "R.atlasroi" in roi][0]

    return {"left": [left_seed, left_rois], "right": [right_seed, right_rois]}


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
