import argparse
from NFACT.base.utils import colours, no_args


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
    option = argparse.ArgumentParser(
        prog="nfact_pp",
        description=print(nfact_pp_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=nfact_pp_example_usage(),
    )
    col = colours()
    option.add_argument(
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        help=f"""{col['red']}REQUIRED FOR ALL MODES:{col['reset']} A list of subjects in text form. If not provided NFACT PP will use all subjects in the study folder. 
        All subjects need full file path to subjects directory""",
    )
    option.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        help=f"{col['red']}REQUIRED FOR ALL MODES:{col['reset']} Directory to save results in",
    )
    option.add_argument(
        "-s",
        "--seed",
        nargs="+",
        dest="seed",
        help=f"{col['pink']}REQUIRED FOR VOLUME/SEED MODE:{col['reset']} A single or list of seeds",
    )
    option.add_argument(
        "-w",
        "--warps",
        dest="warps",
        nargs="+",
        help=f"{col['pink']}REQUIRED FOR VOLUME/SEED MODE:{col['reset']} Path to warps inside a subjects directory (can accept multiple arguments)",
    )
    option.add_argument(
        "-b",
        "--bpx",
        dest="bpx_path",
        help=f"{col['pink']}REQUIRED FOR VOLUME/SEED MODE:{col['reset']} Path to Bedpostx folder inside a subjects directory.",
    )
    option.add_argument(
        "-r",
        "--rois",
        dest="rois",
        nargs="+",
        help=f"""{col['purple']}REQUIRED FOR SEED MODE: {col['reset']}A single or list of ROIS. 
        Use when doing whole brain surface tractography to provide medial wall.""",
    )
    option.add_argument(
        "-f",
        "--file_tree",
        dest="file_tree",
        default=False,
        help=f"""{col['plum']}REQUIRED FOR FILETREE MODE: {col['reset']}Use this option to provide name of predefined file tree to 
        perform whole brain tractography. NFACT_PP currently comes with HCP filetree. See documentation for further information.""",
    )
    option.add_argument(
        "-i",
        "--ref",
        dest="ref",
        help="Standard space reference image. Default is $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz",
    )
    option.add_argument(
        "-t",
        "--target",
        dest="target2",
        default=False,
        help="Name of target. If not given will create a whole mask from reference image",
    )
    option.add_argument(
        "-N",
        "--nsamples",
        dest="nsamples",
        default=1000,
        help="Number of samples per seed used in tractography (default = 1000)",
    )
    option.add_argument(
        "-m",
        "--mm_res",
        dest="mm_res",
        default=2,
        help="Resolution of target image (Default = 2 mm)",
    )
    option.add_argument(
        "-p",
        "--ptx_options",
        dest="ptx_options",
        help="Path to ptx_options file for additional options",
        default=False,
    )
    option.add_argument(
        "-n",
        "--n_cores",
        dest="n_cores",
        help="If should parallel process and with how many cores",
        default=False,
    )
    option.add_argument(
        "-O",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        default=False,
        help="Overwrite previous file structure",
    )
    option.add_argument(
        "-j",
        "--json_stop",
        dest="stop",
        default=False,
        help="""
        File path to a json file containing stop and wtstop masks. 
        Keys must be stoppage_mask and wtstop_mask.
        If filestree is wanted put the word filestree along with a --file_tree [filetree_arg]""",
    )
    no_args(option)

    return vars(option.parse_args())


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
{col['pink']} 
 _   _ ______   ___   _____  _____     ______ ______ 
| \ | ||  ___| /   \ /  __ \|_   _|    | ___ \| ___ \\
|  \| || |_   / /_\ \| /  \/  | |      | |_/ /| |_/ /
|     ||  _|  |  _  || |      | |      |  __/ |  __/ 
| |\  || |    | | | || \__/\  | |      | |    | |    
\_| \_/\_|    \_| |_/ \____/  \_/      \_|    \_|  
{col['reset']} 
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
    {col['purple']}Seed surface mode:{col['reset']}
           nfact_pp --list_of_subjects /home/study/sub_list
               --outdir /home/study   
               --bpx_path /path_to/.bedpostX 
               --seeds /path_to/L.white.32k_fs_LR.surf.gii /path_to/R.white.32k_fs_LR.surf.gii 
               --rois /path_to/L.atlasroi.32k_fs_LR.shape.gii /path_to/R.atlasroi.32k_fs_LR.shape.gii 
               --warps /path_to/stand2diff.nii.gz /path_to/diff2stand.nii.gz 
               --n_cores 3 

    {col['pink']}Volume surface mode:{col['reset']}
            nfact_pp --list_of_subjects /home/study/sub_list  
                --bpx_path /path_to/.bedpostX 
                --seeds /path_to/L.white.nii.gz /path_to/R.white.nii.gz 
                --warps /path_to/stand2diff.nii.gz /path_to/diff2stand.nii.gz 
                --ref MNI152_T1_1mm_brain.nii.gz 
                --target dlpfc.nii.gz

    {col['darker_pink']}Filestree mode:{col['reset']}
        nfact_pp --filestree hcp
            --list_of_subjects /home/study/sub_list  
            --outdir /home/study 
            --n_cores 3 
            \n
"""
