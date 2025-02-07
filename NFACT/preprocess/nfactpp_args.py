import argparse
from NFACT.base.utils import colours, no_args, verbose_help_message


def nfact_pp_args() -> dict:
    """
    Function to get arguements
    to run NFACT pre-processing

    Parameters
    -----------
    None

    Returns
    -------
    dict: dictionary object
        dict of arguments
    """
    base_args = argparse.ArgumentParser(
        prog="nfact_pp",
        description=print(nfact_pp_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    col = colours()
    base_args.add_argument(
        "-hh",
        "--verbose_help",
        dest="verbose_help",
        default=False,
        action="store_true",
        help="""
        Verbose help message.
        Prints help message and example usages
      """,
    )
    base_args.add_argument(
        "-O",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        default=False,
        help="Overwrites previous file structure",
    )
    compulsory_args = base_args.add_argument_group(
        f"{col['deep_pink']}Compulsory Arguments{col['reset']}"
    )
    compulsory_args.add_argument(
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        help="""
        Absolute path to a  list of subjects in text form. 
        All subjects need the absolute file path to subjects directory.
        Consider using nfact_config to help create subject list
        """,
    )
    compulsory_args.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        help="""
        Absolute path to a directory to save results in. 
        nfact_pp creates a folder called nfact_pp in it.
        """,
    )

    file_tree_input = base_args.add_argument_group(
        f"{col['plum']}REQUIRED FOR FILETREE MODE: {col['reset']}"
    )
    file_tree_input.add_argument(
        "-f",
        "--file_tree",
        dest="file_tree",
        default=False,
        help="""Use this option to provide name of predefined file tree to 
        perform whole brain tractography. nfact_pp currently comes with HCP filetree. 
        See documentation for further information.""",
    )
    tractography_input = base_args.add_argument_group(
        f"{col['pink']}Tractography options: {col['reset']}"
    )

    tractography_input.add_argument(
        "-s",
        "--seed",
        nargs="+",
        dest="seed",
        help="""
        Relative path to either a single or multiple seeds. If multiple seeds given
        then include a space between paths. Must be the same across subjects.
        """,
    )
    tractography_input.add_argument(
        "-w",
        "--warps",
        dest="warps",
        nargs="+",
        help="""Relative path to warps inside a subjects directory. 
        Include a space between paths. Must be the same across subjects.
        """,
    )
    tractography_input.add_argument(
        "-b",
        "--bpx",
        dest="bpx_path",
        help="""Relative path to Bedpostx folder inside a subjects directory. 
        Must be the same across subjects""",
    )
    tractography_input.add_argument(
        "-r",
        "--roi",
        dest="roi",
        nargs="+",
        help="""REQUIRED FOR SURFACE MODE: 
        Relative path to a single ROI or multiple ROIS to restrict seeding to (e.g. medial wall masks). 
        Must be the same across subject. ROIS must match number of seeds.
        """,
    )
    tractography_input.add_argument(
        "-sr",
        "--seedref",
        dest="seedref",
        default=False,
        help="""
        Absolute path to a reference volume to define seed space used by probtrackx. 
        Default is MNI space ($FSLDIR/data/standard/MNI152_T1_2mm.nii.gz).
        """,
    )
    tractography_input.add_argument(
        "-t",
        "--target",
        dest="target2",
        default=False,
        help="""
        Absolute path to a target image. 
        If not provided will use the seedref. 
        Default is human MNI ($FSLDIR/data/standard/MNI152_T1_2mm.nii.gz).
        """,
    )
    tractography_input.add_argument(
        "-ns",
        "--nsamples",
        dest="nsamples",
        default=1000,
        help="Number of samples per seed used in tractography. Default is 1000",
    )
    tractography_input.add_argument(
        "-mm",
        "--mm_res",
        dest="mm_res",
        default=2,
        help="""
        Resolution of target image. 
        Default is 2 mm
        """,
    )
    tractography_input.add_argument(
        "-p",
        "--ptx_options",
        dest="ptx_options",
        help="""
        Path to ptx_options file for additional options. 
        Currently doesn't override defaults
        """,
        default=False,
    )

    tractography_input.add_argument(
        "-e",
        "--exclusion",
        dest="exclusion",
        default=False,
        help="""
        Absolute path to an exclusion mask. 
        Will reject pathways passing through locations given by this mask
      """,
    )
    tractography_input.add_argument(
        "-S",
        "--stop",
        dest="stop",
        default=False,
        nargs="*",
        help="""
        Use wtstop and stop in the tractography. 
        Takes an absolute file path to a json file containing stop and wtstop masks, JSON keys must be stopping_mask and wtstop_mask.
        Argument can be used with the --filetree, in that case no json file is needed.
      """,
    )

    parallel_process = base_args.add_argument_group(
        f"{col['darker_pink']}Parallel Processing arguments{col['reset']}"
    )
    parallel_process.add_argument(
        "-n",
        "--n_cores",
        dest="n_cores",
        help="""
        If should parallel process locally and with how many cores. 
        This parallelizes the number of subjects. If n_cores exceeds
        subjects nfact_pp sets this argument to be the number of subjects. 
        If nfact_pp is being used on one subject then this may slow down
        processing.
        """,
        default=False,
    )
    cluster_args = base_args.add_argument_group(
        f"{col['amethyst']}Cluster Arguments{col['reset']}"
    )

    cluster_args.add_argument(
        "-C",
        "--cluster",
        dest="cluster",
        action="store_true",
        default=False,
        help="""Use the cluster enviornment. 
        nfact_pp will check that 
        """,
    )
    cluster_args.add_argument(
        "-cq",
        "--queue",
        dest="cluster_queue",
        default=None,
        help="Cluster queue to submit to",
    )
    cluster_args.add_argument(
        "-cr",
        "--cluster_ram",
        dest="cluster_ram",
        default="60",
        help="The amount of ram that job will take. Default is 60",
    )
    cluster_args.add_argument(
        "-ct",
        "--cluster_time",
        dest="cluster_time",
        default=False,
        help="""
        The amount of time that job will take. 
        nfact_pp will assign a time if none given, depending on cluster gpu status
        """,
    )
    cluster_args.add_argument(
        "-cqos",
        "--cluster_qos",
        dest="cluster_qos",
        default=False,
        help="Set the qos for the cluster. Usually not needed",
    )

    no_args(base_args)
    args = base_args.parse_args()
    if args.verbose_help:
        verbose_help_message(base_args, nfact_pp_example_usage())

    return vars(args)


def nfact_pp_splash() -> str:
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
 _   _ ______   ___   _____  _____     ______ ______ 
| \ | ||  ___| /   \ /  __ \|_   _|    | ___ \| ___ \\
|  \| || |_   / /_\ \| /  \/  | |      | |_/ /| |_/ /
|     ||  _|  |  _  || |      | |      |  __/ |  __/ 
| |\  || |    | | | || \__/\  | |      | |    | |    
\_| \_/\_|    \_| |_/ \____/  \_/      \_|    \_|  
{col["reset"]} 
"""


def nfact_pp_example_usage() -> str:
    """
    Function to return example usage

    Parameters
    ----------
    None

    Returns
    -------
    str: str object
    """
    col = colours()
    return f"""
Example Usage:
    {col["purple"]}Surface mode:{col["reset"]}
           nfact_pp --list_of_subjects /absolute_path/study/sub_list
               --outdir absolute_path/study   
               --bpx_path /relative_path/.bedpostX 
               --seeds /relative_path/L.surf.gii /path_to/R.surf.gii 
               --roi /relative_path/L.exclude_medialwall.shape.gii /path_to/R.exclude_medialwall.shape.gii 
               --warps /relative_path/stand2diff.nii.gz /relative_path/diff2stand.nii.gz 
               --n_cores 3 

    {col["pink"]}Volume mode:{col["reset"]}
            nfact_pp --list_of_subjects /absolute_path/study/sub_list
                --outdir /absolute_path/study   
                --bpx_path /relative_path/.bedpostX 
                --seeds /relative_path/L.white.nii.gz /relative_path/R.white.nii.gz 
                --warps /relative_path/stand2diff.nii.gz /relative_path/diff2stand.nii.gz 
                --seedref absolute_path/MNI152_T1_1mm_brain.nii.gz 
                --target absolute_path/dlpfc.nii.gz

    {col["darker_pink"]}Filestree mode:{col["reset"]}
        nfact_pp --filestree hcp
            --list_of_subjects /absolute_path/study/sub_list  
            --outdir /absolute_path/study 
"""
