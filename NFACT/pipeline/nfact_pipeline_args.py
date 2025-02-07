from NFACT.base.utils import colours, no_args
import argparse


def nfact_parser() -> dict:
    """
    Function to parse command line arguments

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary object
        dict of args
    """

    args = argparse.ArgumentParser(
        prog="nfact",
        description=print(nfact_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    col = colours()
    input_args = args.add_argument_group(
        f"{col['deep_pink']}Pipeline inputs{col['reset']}"
    )
    input_args.add_argument(
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        default=False,
        help="""
        Absolute filepath to a text file containing
        absolute path to subjects. Consider using
        nfact_config to create subject list
        """,
    )
    input_args.add_argument(
        "-s",
        "--seed",
        nargs="+",
        dest="seed",
        default=False,
        help="""
        Relative path to either a single or multiple seeds. If multiple seeds given
        then include a space between paths. Must be the same across subjects.
        """,
    )
    input_args.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        help="""
        Absolute path to a directory to save results in.
        """,
    )
    input_args.add_argument(
        "-n",
        "--folder_name",
        dest="folder_name",
        default="nfact",
        help="""
        Name of output folder. That contains within it
        the nfact_pp, nfact_decomp and nfact_dr folders.
        Default is nfact
        """,
    )
    input_args.add_argument(
        "-c",
        "--config",
        dest="config",
        default=False,
        help="""
        Provide an nfact_config file instead of using command line arguements.
        Configuration files provide control over all parameters of modules
        and can be created using nfact_config -C. 
        If this is provided no other arguments are needed to run nfact as 
        arguments are taken from config file rather than command line.
        """,
    )
    input_args.add_argument(
        "-P",
        "--pp_skip",
        dest="pp_skip",
        action="store_true",
        help="""
        Skips nfact_pp. 
        Pipeline still assumes that data has been pre-processed with nfact_pp before.
        If data hasn't been pre-processed with nfact_pp consider runing modules 
        seperately
        """,
    )
    input_args.add_argument(
        "-Q",
        "--qc_skip",
        dest="qc_skip",
        action="store_true",
        help="Skips nfact_qc.",
    )
    input_args.add_argument(
        "-D",
        "--dr_skip",
        dest="dr_skip",
        action="store_true",
        help="Skips nfact_dr so no dual regression is performed.",
    )
    input_args.add_argument(
        "-O",
        "--overwrite",
        dest="overwrite",
        default=False,
        action="store_true",
        help="Overwirte existing file structure",
    )
    nfact_pp_args = args.add_argument_group(
        f"{col['darker_pink']}nfact_pp inputs{col['reset']}"
    )
    nfact_pp_args.add_argument(
        "-w",
        "--warps",
        dest="warps",
        nargs="+",
        default=False,
        help="""Relative path to warps inside a subjects directory. 
        Include a space between paths. Must be the same across subjects.
        """,
    )
    nfact_pp_args.add_argument(
        "-b",
        "--bpx",
        dest="bpx_path",
        default=False,
        help="""Relative path to Bedpostx folder inside a subjects directory. 
        Must be the same across subjects""",
    )
    nfact_pp_args.add_argument(
        "-r",
        "--roi",
        dest="roi",
        nargs="+",
        default=False,
        help="""REQUIRED FOR SURFACE MODE: 
        Relative path to a single ROI or multiple ROIS to restrict seeding to (e.g. medial wall masks). 
        Must be the same across subject. ROIS must match number of seeds.
        """,
    )
    nfact_pp_args.add_argument(
        "-f",
        "--file_tree",
        dest="file_tree",
        default=False,
        help="""Use this option to provide name of predefined file tree to 
        perform whole brain tractography. nfact_pp currently comes with HCP filetree. 
        See documentation for further information.""",
    )
    nfact_pp_args.add_argument(
        "-sr",
        "--seedref",
        dest="seedref",
        default=False,
        help="""
        Absolute path to a reference volume to define seed space used by probtrackx. 
        Default is MNI space ($FSLDIR/data/standard/MNI152_T1_2mm.nii.gz).
        """,
    )
    nfact_pp_args.add_argument(
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
    nfact_decomp_args = args.add_argument_group(
        f"{col['pink']}nfact_decomp/nfact_dr inputs{col['reset']}"
    )
    nfact_decomp_args.add_argument(
        "-d",
        "--dim",
        default=False,
        dest="dim",
        help="""
        This is compulsory option. 
        Number of dimensions/components to retain
        after running NMF/ICA.  
        """,
    )
    nfact_decomp_args.add_argument(
        "-a",
        "--algo",
        dest="algo",
        default="NMF",
        help="""
        Which decomposition algorithm to run. 
        Options are: NMF (default), or ICA. This is case
        insensitive
        """,
    )
    nfact_decomp_args.add_argument(
        "-rf",
        "--rf_decomp",
        dest="roi",
        default=False,
        help="""
        Absolute path to a text file containing the  
        absolute path ROI(s) paths to restrict seeding to 
        (e.g. medial wall masks). This is not needed if
        seeds are not surfaces. If used nfact_pp then this
        is the roi_for_decomp.txt file in the nfact_pp
        directory. This option is not needed if
        the pipeline is being ran from nfact_pp onwards.
        """,
    )
    nfact_Qc_args = args.add_argument_group(
        f"{col['purple']}nfact_Qc inputs{col['reset']}"
    )
    nfact_Qc_args.add_argument(
        "--threshold",
        dest="threshold",
        default=2,
        help="Z score value to threshold hitmaps.",
    )

    no_args(args)
    return {
        "args": vars(args.parse_args()),
        "input": input_args._group_actions,
        "nfact_pp": nfact_pp_args._group_actions,
        "decomp": nfact_decomp_args._group_actions,
        "qc": nfact_Qc_args._group_actions,
    }


def extract_group_args(group: list, args_dict: dict):
    """
    Function to extract group
    arguments from a given dictionary

    Parameters
    ----------
    group: list
        a list of argparse._StoreAction
    args_dict: dict

    Returns
    -------
    dict
    """
    return {arg.dest: args_dict[arg.dest] for arg in group if arg.dest in args_dict}


def sort_args(
    args_dictionary: dict,
    input_args: list,
    nfact_pp_args: list,
    decomp_args: list,
    qc_args: list,
) -> dict:
    """
    Function to sort arguments into
    a dictionary by group.

    Parameters
    ----------
    args_dictionary: dict
        dictionary of arguments to sort
        by group
    input_args: list
        a list of argparse._StoreAction
    nfact_pp_args: list
        a list of argparse._StoreAction
    decomp_args: list
        a list of argparse._StoreAction
    qc_args: list
        a list of argparse._StoreAction


    Returns
    -------
    dict: dictionary object
        dictionary of sorted command line
        arguments.
    """

    return {
        "input": extract_group_args(input_args, args_dictionary),
        "pre_process": extract_group_args(nfact_pp_args, args_dictionary),
        "decomp": extract_group_args(decomp_args, args_dictionary),
        "qc": extract_group_args(qc_args, args_dictionary),
    }


def nfact_args():
    """
    Function to parse NFACT
    arguments by group.

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary
       dictionary object of parsed
       command line arguments
    """

    args = nfact_parser()
    return sort_args(
        args["args"], args["input"], args["nfact_pp"], args["decomp"], args["qc"]
    )


def nfact_splash() -> str:
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
 _   _ ______   ___   _____  _____    
| \ | ||  ___| /   \ /  __ \|_   _|    
|  \| || |_   / /_\ \| /  \/  | |      
|     ||  _|  |  _  || |      | |    
| |\  || |    | | | || \__/\  | |    
\_| \_/\_|    \_| |_/ \____/  \_/ 
{col["reset"]} 
"""
