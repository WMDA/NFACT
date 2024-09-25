import argparse
from NFACT.NFACT_base.utils import colours


def nfactdr_args() -> dict:
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
        prog="nfact_dr",
        description=print(nfact_dr_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    col = colours()
    args.add_argument(
        "-p",
        "--ptxdir",
        nargs="+",
        dest="ptxdir",
        help="List of file paths to probtrackx directories. If not provided will then --list_ofsubjects must be provided",
    )
    args.add_argument(
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        help="Filepath to a list of subjects. If not given then --ptxdir must be directories.",
    )
    args.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        help=f"{col['red']}REQUIRED{col['reset']}: Path to output directory",
    )
    args.add_argument(
        "-a",
        "--algo",
        dest="algo",
        help=f"{col['red']}REQUIRED{col['reset']}: Which NFACT algorithm to perform dual regression on",
    )
    args.add_argument(
        "--seeds",
        "-s",
        dest="seeds",
        help=f"{col['red']}REQUIRED{col['reset']}: File of seeds used in NFACT_PP/probtrackx",
    )
    args.add_argument(
        "-N",
        "--normalise",
        dest="normalise",
        action="store_true",
        default=False,
        help="normalise components by scaling",
    )

    return vars(args.parse_args())


def nfact_dr_splash() -> str:
    """
    Function to return NFACT DR splash

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
 _   _ ______   ___   _____  _____  ______ ______ 
| \ | ||  ___| / _ \ /  __ \|_   _| |  _  \| ___ \\
|  \| || |_   / /_\ \| /  \/  | |   | | | || |_/ /
| . ` ||  _|  |  _  || |      | |   | | | ||    / 
| |\  || |    | | | || \__/\  | |   | |/ / | |\ \ 
\_| \_/\_|    \_| |_/ \____/  \_/   |___/  \_| \_|
{col['reset']}                                                                              
"""
