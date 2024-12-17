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
        help=f"{col['red']}REQUIRED:{col['reset']} Path to nfact output folder",
    )
    args.add_argument(
        "-d",
        "--dim",
        dest="dim",
        help=f"{col['red']}REQUIRED:{col['reset']} Number of dimensions/components",
    )
    args.add_argument(
        "-a",
        "--algo",
        dest="algo",
        default="NMF",
        help=f"{col['red']}REQUIRED:{col['reset']}What algorithm to qc. Options are: NMF (default), or ICA.",
    )
    args.add_argument(
        "-t",
        "--threshold",
        dest="threshold",
        default=2,
        help="Threshold value for z scoring the normalised image",
        type=int,
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
{col['pink']} 
 _   _ ______   ___   _____  _____  
| \ | ||  ___| / _ \ /  __ \|_   _|    ___     ____ 
|  \| || |_   / /_\ \| /  \/  | |     / _ \   / ___|
| . ` ||  _|  |  _  || |      | |    | | | | | |    
| |\  || |    | | | || \__/\  | |    | |_| | | |___ 
\_| \_/\_|    \_| |_/ \____/  \_/     \__\_\  \____|
{col['reset']} 
"""


def nfact_Qc_usage():
    """
    Function to return NFACT
    decomp usage

    Parameteres
    -----------
    None

    Returns
    ------
    None
    """
    col = colours()
    return f"""
{col['darker_pink']}Basic NMF with volume seeds usage:{col['reset']}
    nfact_decomp --list_of_subjects /absolute path/sub_list \ 
                 --seeds /absolute path/seeds.txt \ 
                 --dim 50

{col['darker_pink']}Basic NMF usage with surface seeds:{col['reset']}
    nfact_decomp --list_of_subjects /absolute path/sub_list \ 
                 --seeds /absolute path/seeds.txt \ 
                 --medial_wall /path/to/medial/wall
                 --dim 50

{col['darker_pink']}ICA with config file usage:{col['reset']}
    nfact_decomp --list_of_subjects /absolute path/sub_list \ 
                 --seeds /absolute path/seeds.txt \ 
                 --outdir /absolute path/study_directory \ 
                 --algo ICA \ 
                 --nfact_config /path/to/config/file

{col['darker_pink']}Advanced ICA Usage:{col['reset']}
    nfact_decomp --list_of_subjects /absolute path/sub_list \ 
                 --seeds /absolute path/seeds.txt \ 
                 --outdir /absolute path/study_directory \ 
                 --algo ICA \ 
                 --migp 1000 \ 
                 --dim 100 \ 
                 --normalise \ 
                 --wta \ 
                 --wat_zthr 0.5
"""
