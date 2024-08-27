from NFACT.NFACT_base.utils import colours
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
        help="Filepath to a list of subjects.",
    )
    input_args.add_argument(
        "-t",
        "--test",
        dest="test",
        help="test.",
    )

    nfact_pp_args = args.add_argument_group("nfact_pp")
    nfact_pp_args.add_argument(
        "-i",
        "--image_standard_space",
        dest="ref",
        required=True,
        help=f"{col['red']}REQUIRED{col['reset']} Standard space reference image",
    )

    return {
        "args": vars(args.parse_args()),
        "input": input_args,
        "nfact_pp": nfact_pp_args,
    }


def sort_args(args_dictionary: dict, input_args: list, nfact_pp_args: list) -> dict:
    """
    Function to sort arguments into
    a dictionary by group.

    Parameters
    ----------
    args_dictionary: dict
        dictionary of arguments to sort
        by group
    inpit_args: object


    """
    print(type(input_args._group_actions[0]))
    return {
        "input": {
            arg.dest: args_dictionary[arg.dest]
            for arg in input_args._group_actions
            if arg.dest in args_dictionary
        },
        "nfact_pp": {
            arg.dest: args_dictionary[arg.dest]
            for arg in nfact_pp_args._group_actions
            if arg.dest in args_dictionary
        },
    }


def nfact_args():
    """
    Function to parse NFACT
    arguments by group.
    """

    args = nfact_parser()
    return sort_args(args["args"], args["input"], args["nfact_pp"])


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
