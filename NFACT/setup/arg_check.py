from NFACT.utils.utils import error_and_exit


def check_complusory_arguments(args: dict) -> None:
    """
    Function to check that ptx folder
    given

    Parameters
    ----------
    args: dict
        dictionary of command line
        arguments

    Returns
    -------
    None
    """

    if not args["ptxdir"] and not args["list_of_subjects"]:
        error_and_exit(
            False,
            "No subjects given. Please provide either --ptx_folder or --list_of_subjects",
        )
    if not args["dim"]:
        error_and_exit(False, "No dimensions given. Please provide either --dim")
    if not args["seeds"]:
        error_and_exit(False, "No seeds provided. Please provide --seeds")
    if not args["outdir"]:
        error_and_exit(False, "No output directory provided. Please specifiy --outdir")


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
    implemented_decomp_methods = ["nfm", "ica"]
    if algo.lower() not in implemented_decomp_methods:
        error_and_exit(
            False,
            f"{algo} is not implemented in NFACT. NFACT currently implements ICA and NFM. Please specify with --algo",
        )
    return algo.lower()


def process_command_args(args: dict) -> dict:
    """
    Function to process command line arguments.

    Parameters
    ----------
    args: dict
        dictionary of command line
        arguments

    Returns
    -------
    args: dict
    """
    if ".0" in args["dim"]:
        args["dim"] = float(args["dim"])
    try:
        args["dim"] = int(args["dim"])
    except Exception:
        error_and_exit(
            False,
            f"Dimmensions must be a interger value. {args['dim']} is not a interger type",
        )
    if args["wta_zthr"]:
        try:
            args["wta_zthr"] = float(args["wta_zthr"])
        except Exception:
            error_and_exit(
                False,
                f"wta_thr must be a float value. {args['wta_zthr']} is not a float",
            )

    if ".0" in args["migp"]:
        args["migp"] = float(args["migp"])
    if args["algo"] != "nfm":
        if args["migp"]:
            try:
                args["migp"] = int(args["migp"])
            except Exception:
                error_and_exit(
                    False,
                    f"migp must be a interger value. {args['migp']} is not a interger type",
                )
    if args["algo"] == "nfm":
        args["migp"] = None
    return args
