from NFACT.base.utils import error_and_exit


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
    args["dim"] = str(args["dim"])
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

    args["migp"] = str(args["migp"])
    if ".0" in args["migp"]:
        args["migp"] = float(args["migp"])

    if args["algo"] != "nmf":
        if args["migp"]:
            try:
                args["migp"] = int(args["migp"])
            except Exception:
                error_and_exit(
                    False,
                    f"MIGP must be a interger value. {args['migp']} is not a interger type",
                )
    if args["algo"] == "nmf":
        args["migp"] = None
    return args
