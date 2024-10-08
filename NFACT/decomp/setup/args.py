import argparse
from NFACT.base.utils import colours, no_args


def nfact_decomp_args() -> dict:
    """
    Function to define cmd arguments

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary
        dictionary of cmd arguments
    """
    args = argparse.ArgumentParser(
        prog="nfact",
        description=print(nfact_decomp_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    col = colours()
    args.add_argument(
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        help=f"{col['red']}REQUIRED:{col['reset']} Filepath to a list of subjects. List can contain a single subject.",
    )
    args.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        help=f"{col['red']}REQUIRED:{col['reset']} Path to output folder",
    )
    args.add_argument(
        "-d",
        "--dim",
        dest="dim",
        help=f"{col['red']}REQUIRED:{col['reset']} Number of dimensions/components",
    )

    args.add_argument(
        "--seeds",
        "-s",
        dest="seeds",
        help=f"{col['red']}REQUIRED:{col['reset']} File of seeds used in NFACT_PP/probtrackx",
    )
    args.add_argument(
        "-m",
        "--migp",
        dest="migp",
        default="1000",
        help="MELODIC's Incremental Group-PCA dimensionality (default is 1000)",
    )
    args.add_argument(
        "-a",
        "--algo",
        dest="algo",
        default="ICA",
        help="What algorithm to run. Options are: ICA (default), or NMF.",
    )
    args.add_argument(
        "-W",
        "--wta",
        dest="wta",
        action="store_true",
        default=False,
        help="Save winner-takes-all maps",
    )
    args.add_argument(
        "-z",
        "--wta_zthr",
        dest="wta_zthr",
        default=0.0,
        help="Winner-takes-all threshold (default=0.)",
    )
    args.add_argument(
        "-N",
        "--normalise",
        dest="normalise",
        action="store_true",
        default=False,
        help="normalise components by scaling",
    )
    args.add_argument(
        "-S",
        "--sign_flip",
        dest="sign_flip",
        action="store_true",
        default=False,
        help="sign flip components",
    )
    args.add_argument(
        "-O",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        default=False,
        help="Overwrite previous file structure. Useful if wanting to perform multiple GLMs or ICA and NFM",
    )
    args.add_argument(
        "-c",
        "--config",
        dest="config",
        default=False,
        help="Provide config file to change hyperparameters for ICA and NFM. Please see sckit learn documentation for NFM and FASTICA for further details",
    )
    no_args(args)
    return vars(args.parse_args())


def nfact_decomp_splash() -> str:
    """
    Function to return NFACT splash

    Parameters
    ----------
    None

    Returns
    -------
    str: splash
    """
    col = colours()
    return f"""
{col['pink']} 
 _   _ ______   ___   _____  _____  ______  _____  _____  _____ ___  ___ _____ 
| \ | ||  ___| / _ \ /  __ \|_   _| |  _  \|  ___|/  __ \|  _  ||  \/  || ___ \\
|  \| || |_   / /_\ \| /  \/  | |   | | | || |__  | /  \/| | | || .  . || |_/ /
| . ` ||  _|  |  _  || |      | |   | | | ||  __| | |    | | | || |\/| ||  __/ 
| |\  || |    | | | || \__/\  | |   | |/ / | |___ | \__/\\\ \_/ /| |  | || |    
\_| \_/\_|    \_| |_/ \____/  \_/   |___/  \____/  \____/ \___/ \_|  |_/\_| 
{col['reset']} 
"""
