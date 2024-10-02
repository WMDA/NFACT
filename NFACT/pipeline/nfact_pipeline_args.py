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
    input_args = args.add_argument_group("Inputs")
    input_args.add_argument(
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        default=False,
        help=f"{col['red']}REQUIRED{col['reset']} Filepath to a list of subjects.",
    )
    input_args.add_argument(
        "-s",
        "--seed",
        nargs="+",
        dest="seed",
        default=False,
        help=f"{col['red']}REQUIRED{col['reset']} A single or list of seeds",
    )
    input_args.add_argument(
        "-c",
        "--config",
        dest="config",
        default=False,
        help="An nfact_config file. If this is provided no other arguments are needed.",
    )
    input_args.add_argument(
        "-S",
        "--skip",
        dest="skip",
        action="store_true",
        help="Skips NFACT_PP. Pipeline still assumes that NFACT_PP has been ran before.",
    )
    input_args.add_argument(
        "-o", "--outdir", dest="outdir", help="Path to where to create an output folder"
    )

    nfact_pp_args = args.add_argument_group("PP")
    nfact_pp_args.add_argument(
        "-i",
        "--image_standard_space",
        dest="ref",
        default=False,
        help=f"{col['red']}REQUIRED{col['reset']} Standard space reference image",
    )
    nfact_pp_args.add_argument(
        "-b",
        "--bpx",
        dest="bpx_path",
        default=False,
        help="Path to Bedpostx folder inside a subjects directory.",
    )

    nfact_pp_args.add_argument(
        "-w",
        "--warps",
        dest="warps",
        nargs="+",
        default=False,
        help="Path to warps inside a subjects directory (can accept multiple arguments)",
    )
    nfact_pp_args.add_argument(
        "-r",
        "--rois",
        dest="rois",
        nargs="+",
        default=False,
        help="A single or list of ROIS",
    )
    nfact_pp_args.add_argument(
        "-t",
        "--target",
        dest="target2",
        default=False,
        help="Path to target image. If not given will create a whole mask from reference image",
    )
    nfact_decomp_args = args.add_argument_group("decomp")
    nfact_decomp_args.add_argument(
        "-d", "--dim", default=False, dest="dim", help="Number of dimensions/components"
    )
    nfact_decomp_args.add_argument(
        "-a",
        "--algo",
        default="ICA",
        help="What algorithm to run. Options are: ICA (default), or NMF.",
    )
    no_args(args)
    return {
        "args": vars(args.parse_args()),
        "input": input_args._group_actions,
        "nfact_pp": nfact_pp_args._group_actions,
        "decomp": nfact_decomp_args._group_actions,
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
    args_dictionary: dict, input_args: list, nfact_pp_args: list, decomp_args: list
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
    return sort_args(args["args"], args["input"], args["nfact_pp"], args["decomp"])


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
{col['pink']} 
 _   _ ______   ___   _____  _____    
| \ | ||  ___| /   \ /  __ \|_   _|    
|  \| || |_   / /_\ \| /  \/  | |      
|     ||  _|  |  _  || |      | |    
| |\  || |    | | | || \__/\  | |    
\_| \_/\_|    \_| |_/ \____/  \_/ 
{col['reset']} 
"""
