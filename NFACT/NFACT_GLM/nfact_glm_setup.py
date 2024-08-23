from NFACT.NFACT_base.utils import error_and_exit
import os


def check_compulsory_arguments(args: dict) -> None:
    """
    Function to check that complusory arguments
    are provided.

    Parameters
    ----------
    args: dict
        A dictionary of args

    Returns
    -------
    None
    """

    compulsory_arguments = ["nfact_dir", "type_of_decomp", "design_matrix", "contrast"]

    [
        error_and_exit(
            args[key], f"{key} is not provided. Please use --{key} to specify"
        )
        for key in compulsory_arguments
    ]


def check_nfactdr(path: str, algo: str) -> None:
    """
    Function to check the nfactdr directory
    and that dual regression has been performed.
    """
    error_and_exit(
        os.path.exists(path),
        "nfact_dr does not exist. nfact glm needs dual regress components to perform GLM. use nfact_dr --help for further details",
    )
    error_and_exit(
        (False if not os.listdir(os.path.join(path, algo)) else True),
        "Unable to find dual regression components. Please check dual regression has been performed.",
    )
