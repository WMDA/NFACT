import argparse
from NFACT.base.utils import colours, no_args, verbose_help_message


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
        "--roi",
        "-r",
        dest="roi",
        default=False,
        help=f"""
        {col["red"]}REQUIRED FOR SURFACE SEEDS:{col["reset"]}
        Txt file with ROI(s) paths to restrict seeding to (e.g. medial wall masks).
        """,
    )
    args.add_argument(
        "-a",
        "--algo",
        dest="algo",
        default="NMF",
        help="What algorithm to run. Options are: NMF (default), or ICA.",
    )
    args.add_argument(
        "-c",
        "--components",
        dest="components",
        default="1000",
        help=f"{col['darker_pink']}REQUIRED FOR ICA:{col['reset']} Components for the PCA (default is 1000)",
    )
    args.add_argument(
        "-p",
        "--pca_type",
        dest="pca_type",
        default="pca",
        help=f"""{col["darker_pink"]}REQUIRED FOR ICA:{col["reset"]} Type of PCA to do before ICA. Default is PCA which is sckitlearn's PCA. 
        Other option is migp (MELODIC's Incremental Group-PCA dimensionality). This is case insensitive""",
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
        help="Normalises components by zscoring.",
    )
    args.add_argument(
        "-S",
        "--sign_flip",
        dest="sign_flip",
        action="store_false",
        default=True,
        help="Don't Sign flip components of ICA",
    )
    args.add_argument(
        "-O",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        default=False,
        help="Overwrite previous file structure",
    )
    args.add_argument(
        "-n",
        "--nfact_config",
        dest="config",
        default=False,
        help="Provide config file to change hyperparameters for ICA and NMF. Please see sckit learn documentation for NMF and FASTICA for further details",
    )
    args.add_argument(
        "-hh",
        "--verbose_help",
        dest="verbose_help",
        default=False,
        action="store_true",
        help="""
        Prints help message and example usages
      """,
    )
    no_args(args)
    options = args.parse_args()
    if options.verbose_help:
        verbose_help_message(args, nfact_decomp_usage())
    return vars(options)


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
{col["pink"]} 
 _   _ ______   ___   _____  _____  ______  _____  _____  _____ ___  ___ _____ 
| \ | ||  ___| / _ \ /  __ \|_   _| |  _  \|  ___|/  __ \|  _  ||  \/  || ___ \\
|  \| || |_   / /_\ \| /  \/  | |   | | | || |__  | /  \/| | | || .  . || |_/ /
| . ` ||  _|  |  _  || |      | |   | | | ||  __| | |    | | | || |\/| ||  __/ 
| |\  || |    | | | || \__/\  | |   | |/ / | |___ | \__/\\\ \_/ /| |  | || |    
\_| \_/\_|    \_| |_/ \____/  \_/   |___/  \____/  \____/ \___/ \_|  |_/\_| 
{col["reset"]} 
"""


def nfact_decomp_usage():
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
{col["darker_pink"]}Basic NMF with volume seeds usage:{col["reset"]}
    nfact_decomp --list_of_subjects /absolute path/sub_list \ 
                 --seeds /absolute path/seeds.txt \ 
                 --dim 50

{col["darker_pink"]}Basic NMF usage with surface seeds:{col["reset"]}
    nfact_decomp --list_of_subjects /absolute path/sub_list \ 
                 --seeds /absolute path/seeds.txt \ 
                 --roi /path/to/rois
                 --dim 50

{col["darker_pink"]}ICA with config file usage:{col["reset"]}
    nfact_decomp --list_of_subjects /absolute path/sub_list \ 
                 --seeds /absolute path/seeds.txt \ 
                 --outdir /absolute path/study_directory \ 
                 --algo ICA \ 
                 --nfact_config /path/to/config/file

{col["darker_pink"]}Advanced ICA Usage:{col["reset"]}
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
