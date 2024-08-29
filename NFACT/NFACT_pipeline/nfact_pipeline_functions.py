from NFACT.NFACT_base.utils import error_and_exit
from NFACT.NFACT_base.filesystem import read_file_to_list, write_to_file
import os


def pipeline_args_check(args: dict):
    """
    Function to check that compulsory
    args are given.

    Parameters
    ----------
    args: dict
        command line arguments

    Returns
    -------
    None
    """
    non_complusory = ["target2", "config"]
    for val in args.keys():
        [
            error_and_exit(
                args[val][arg], f"{arg} is not defined. Please define with --{arg}"
            )
            for arg in args[val].keys()
            if arg not in non_complusory
        ]


def build_args(args_dict: dict, module_dict: dict) -> dict:
    """
    Fuction to build out arguments
    from args dict to module dict

    Parameters
    ----------
    args_dict: dict
        dictionary of command line
        arguments
    module_dict: dict
        dict of module arguments

    Returns
    -------
    module_dict: dict
        dictionary of updated module
        arguments
    """
    for key in module_dict:
        if key in args_dict:
            module_dict[key] = args_dict[key]
    return module_dict


def build_module_arguments(module_dict: dict, args: dict, key: str):
    """
    Function to build out a module command line
    arguments.

    Parameters
    ----------
    module_dict: dict
        dict of module arguments
    args_dict: dict
        dictionary of command line
        arguments
    key: str
        str of key for argument dict
        to build out module dictionary

    Returns
    -------
    dict: dictionary
        dictionary of module arguments

    """
    module_dict = build_args(args["input"], module_dict)
    return build_args(args[key], module_dict)


def convert_str_to_bool(val) -> any:
    """
    Converts string instances of 'True' and 'False'

    Parameters
    ----------
    val: str
       string value

    Returns
    -------
    any: mixed
       either True, False
       or the original string
       type.

    """
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    return val


def process_dictionary_arguments(dictionary_to_process: dict) -> dict:
    """
    Clean str instances of bool to
    actual bool type

    Parameters
    ----------
    dictionary_to_process : dict
        The dictionary to process.

    Returns
    -------
    dict
        The dictionary with strings
        'True' and 'False' converted to bool
        type.
    """
    return {
        key: convert_str_to_bool(value) if type(value) == str else value
        for key, value in dictionary_to_process.items()
    }


def write_decomp_list(
    file_path: str, out_dir_name: str, nfact_tmp_location: str
) -> None:
    """
    Function to write to a file
    the subjects  omatrix2 location.

    Parameters
    ----------
    file_path: str
        str to sub list file
    out_dir_name: str
        str of the name of
        the output directory of nfact_pp
    nfact_tmp_location: str
        path of nfact_tmp location

    Returns
    -------
    None
    """
    files = read_file_to_list(file_path)
    omatrix_2_paths = [os.path.join(file, out_dir_name, "omatrix2\n") for file in files]
    omatrix_2_paths.sort()

    write_to_file(
        nfact_tmp_location,
        "nfact_decomp_sub_list",
        omatrix_2_paths,
        text_is_list=True,
    )
