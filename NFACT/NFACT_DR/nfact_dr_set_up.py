from NFACT.NFACT_base.setup import check_study_folder_exists
from NFACT.NFACT_base.utils import error_and_exit, colours

import os


def check_nfact_directory(nfact_directory: str, algo: str):
    """
    Function to check the NFACT directory has all
    the
    """
    error_and_exit(
        check_study_folder_exists(
            nfact_directory,
            "NFACT directory does not exist. Check the given path and that group level decompoisition has been ran.",
        )
    )
    error_and_exit(
        os.path.exists(os.path.join(nfact_directory, "components", algo, "decomp"))
        or os.listdir(os.path.join(nfact_directory, "components", algo, "decomp")),
        "No components found. Please check that decomposition has been ran.",
    )
