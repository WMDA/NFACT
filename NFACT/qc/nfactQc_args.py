import argparse
from NFACT.base.utils import colours, no_args


def nfact_qc_args() -> dict:
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
        description=print(nfact_Qc_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    col = colours()
    args.add_argument(
        "-n",
        "--nfact_folder",
        dest="nfact_folder",
        help=f"""{col['red']}REQUIRED:{col['reset']} 
        Absolute path to nfact_decomp output folder.
        nfact_Qc folder is also saved within this
        folder.
        """,
    )
    args.add_argument(
        "-d",
        "--dim",
        dest="dim",
        help=f"""{col['red']}REQUIRED:{col['reset']} 
        Number of dimensions/components that 
        was used to generate nfact_decomp image
        """,
    )
    args.add_argument(
        "-a",
        "--algo",
        dest="algo",
        default="NMF",
        help=f"""{col['red']}REQUIRED:{col['reset']}
        Which algorithm to run qulatiy control on. 
        Options are: NMF (default), or ICA.
        """,
    )
    args.add_argument(
        "-t",
        "--threshold",
        dest="threshold",
        default=2,
        help="""
        Threshold value for z scoring the number of times
        a component comes up in a voxel in the image.
        Values below this z score are treated as noise and 
        discarded in the non raw image. 
        """,
    )
    args.add_argument(
        "-O",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        help="Overwite previous QC",
    )
    no_args(args)
    return vars(args.parse_args())


def nfact_Qc_splash() -> str:
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
{col["pink"]} 
 _   _ ______   ___   _____  _____     ___     ____ 
| \ | ||  ___| / _ \ /  __ \|_   _|   / _ \   / ___|
|  \| || |_   / /_\ \| /  \/  | |    | | | | | | 
| . ` ||  _|  |  _  || |      | |    | | | | | |    
| |\  || |    | | | || \__/\  | |    | |_| | | |___ 
\_| \_/\_|    \_| |_/ \____/  \_/     \__\_\  \____|
{col["reset"]} 
"""
