import argparse
from NFACT.base.utils import colours, no_args


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
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        help=f"{col['red']}REQUIRED:{col['reset']} Filepath to a list of subjects",
    )
    args.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        help=f"{col['red']}REQUIRED:{col['reset']}  Path to output directory",
    )
    args.add_argument(
        "-a",
        "--algo",
        dest="algo",
        help=f"{col['red']}REQUIRED:{col['reset']} Which NFACT algorithm to perform dual regression on",
    )
    args.add_argument(
        "--seeds",
        "-s",
        dest="seeds",
        help=f"{col['red']}REQUIRED:{col['reset']} File of seeds used in NFACT_PP/probtrackx",
    )
    args.add_argument(
        "-n",
        "--nfact_decomp_dir",
        dest="nfact_decomp_dir",
        help=f"{col['plum']}REQUIRED IF NFACT_DECOMP:{col['reset']} Filepath to the NFACT_decomp directory. Use this if you have ran NFACT decomp",
    )
    args.add_argument(
        "-d",
        "--decomp_dir",
        dest="decomp_dir",
        help=f"""{col['plum']}REQUIRED IF NOT NFACT_DECOMP:{col['reset']} Filepath to decomposition components. 
        WARNING NFACT decomp expects components to be named in a set way. See documentation for further info.""",
    )
    args.add_argument(
        "-N",
        "--normalise",
        dest="normalise",
        action="store_true",
        default=False,
        help="normalise components by scaling",
    )
    no_args(args)
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
