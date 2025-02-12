import argparse
from NFACT.base.utils import colours, no_args, verbose_help_message
from NFACT.base.base_args import set_up_args, base_arguments


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
    base_args = argparse.ArgumentParser(
        prog="nfact_decomp",
        description=print(nfact_decomp_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    col = colours()
    base_arguments(base_args)
    set_up_args(base_args, col)

    decomp_input = base_args.add_argument_group(
        f"{col['plum']}Decomposition inputs{col['reset']}"
    )
    decomp_input.add_argument(
        "--seeds",
        "-s",
        dest="seeds",
        help="""
        Absolute path to a text file of seed(s) 
        used in nfact_pp/probtrackx.
        If used nfact_pp this is the seeds_for_decomp.txt
        in the nfact_pp directory.
        """,
    )
    decomp_input.add_argument(
        "--roi",
        "-r",
        dest="roi",
        default=False,
        help="""
        Absolute path to a text file containing the  
        absolute path ROI(s) paths to restrict seeding to 
        (e.g. medial wall masks). This is not needed if
        seeds are not surfaces. If used nfact_pp then this
        is the roi_for_decomp.txt file in the nfact_pp
        directory.
        """,
    )
    decomp_input.add_argument(
        "-n",
        "--nfact_config",
        dest="config",
        default=False,
        help="""
        Absolute path to a configuration file.
        Congifuration file provides available hyperparameters for ICA and NMF. 
        Use nfact_config -D to create a config file.
        Please see sckit learn documentation for NMF and FASTICA for further details
        """,
    )
    decomp_args = base_args.add_argument_group(
        f"{col['pink']}Decomposition options{col['reset']}"
    )
    decomp_args.add_argument(
        "-d",
        "--dim",
        dest="dim",
        help="""
        This is compulsory option. 
        Number of dimensions/components to retain
        after running NMF/ICA.  
        """,
    )
    decomp_args.add_argument(
        "-a",
        "--algo",
        dest="algo",
        default="NMF",
        help="""Which decomposition algorithm to run. 
        Options are: NMF (default), or ICA. This is case
        insensitive
        """,
    )
    output_args = base_args.add_argument_group(
        f"{col['darker_pink']}Output options{col['reset']}"
    )
    output_args.add_argument(
        "-W",
        "--wta",
        dest="wta",
        action="store_true",
        default=False,
        help="""
        Option to create and save winner-takes-all maps.
        """,
    )
    output_args.add_argument(
        "-z",
        "--wta_zthr",
        dest="wta_zthr",
        default=0.0,
        help="Winner-takes-all threshold. Default is 0",
    )
    output_args.add_argument(
        "-N",
        "--normalise",
        dest="normalise",
        action="store_true",
        default=False,
        help="""
        Z scores component values
        and saves map. This is useful for visualization
        """,
    )
    ica_options = base_args.add_argument_group(
        f"{col['purple']}ICA options{col['reset']}"
    )
    ica_options.add_argument(
        "-c",
        "--components",
        dest="components",
        default="1000",
        help="""
        Number of component to be 
        retained following the PCA. 
        Default is 1000
        """,
    )
    ica_options.add_argument(
        "-p",
        "--pca_type",
        dest="pca_type",
        default="pca",
        help="""
        Which type of PCA to do before ICA. 
        Options are 'pca' which is sckit learns default PCA
        or 'migp' (MELODIC's Incremental Group-PCA dimensionality).
        Default is 'pca' as for most
        cases 'migp' is slow and not needed.
        Option is case insensitive.
        """,
    )

    ica_options.add_argument(
        "-S",
        "--sign_flip",
        dest="sign_flip",
        action="store_false",
        default=True,
        help="""
        nfact_decomp by default sign flips the ICA 
        distribution to reduce the number of negative values.
        Use this option to stop the sign_flip 
        """,
    )

    no_args(base_args)
    args = base_args.parse_args()
    if args.verbose_help:
        verbose_help_message(base_args, nfact_decomp_usage())
    return vars(args)


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
                 --roi /absolute path/rois
                 --dim 50

{col["darker_pink"]}ICA with config file usage:{col["reset"]}
    nfact_decomp --list_of_subjects /absolute path/sub_list \ 
                 --seeds /absolute path/seeds.txt \ 
                 --outdir /absolute path/study_directory \ 
                 --algo ICA \ 
                 --nfact_config /absolute path/nfact_config.decomp

{col["darker_pink"]}Advanced ICA Usage:{col["reset"]}
    nfact_decomp --list_of_subjects /absolute path/sub_list \ 
                 --seeds /absolute path/seeds.txt \ 
                 --outdir /absolute path/study_directory \ 
                 --algo ICA \ 
                 --components 1000 \ 
                 --pca_type mipg
                 --dim 100 \ 
                 --normalise \ 
                 --wta \ 
                 --wta_zthr 0.5
"""
