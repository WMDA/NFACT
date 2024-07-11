import os
from NFACT.utils.utils import error_and_exit


def create_output_folder(out_folder: str) -> None:
    """
    Function to create output folder.
    If can't it errors out.

    Parameters
    ----------
    out_folder: str
        string of path to output folder

    Returns
    -------
    None
    """

    try:
        os.mkdir(out_folder)
    except Exception as e:
        error_and_exit(False, f"Unable to create output folder due {e}")
