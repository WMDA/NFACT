from NFACT.NFACT_base.utils import error_and_exit


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

    compulsory_arguments = ["nfact_dir", "type_of_decomp", "design_matrix", "contrasts"]

    [
        error_and_exit(
            args[key], f"{key} is not provided. Please use --{key} to specify"
        )
        for key in compulsory_arguments
    ]
