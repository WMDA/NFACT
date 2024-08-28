from NFACT.NFACT_base.utils import error_and_exit


def pipeline_args_check(args: dict):
    """
    Function to check that compulsory
    args are given.

    Parameters
    ----------
    args: dict
        command line arguments

    Returns
    -------
    None
    """
    non_complusory = ["target2"]
    for val in args.keys():
        [
            error_and_exit(
                args[val][arg], f"{arg} is not defined. Please define with --{arg}"
            )
            for arg in args[val].keys()
            if arg not in non_complusory
        ]
