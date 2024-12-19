from NFACT.base.utils import error_and_exit
from NFACT.base.filesystem import read_file_to_list, write_to_file
import os


def non_compulsory_arguments(
    standard: bool = False, skip: bool = False, volume: bool = False, file_tree=False
) -> list:
    """
    Function to return what are non
    complusory arguments.

    Parameters
    ----------
    standard: bool
        returns standard non
        compulsory arguments
        Default is False.
    skip: bool
        returns skip non
        compulsory arguments
        Default is False.
    volume: bool
        returns volume non
        compulsory arguments
        Default is False.
    file_tree: bool
        if file_tree option
        is used.
        Default is False.

    Returns
    -------
    list: list object
        List of non
        compulsory arguments
    """
    standard_args = ["target2", "config", "skip"]
    if standard:
        return standard_args
    if skip:
        return standard_args + ["ref", "bpx_path", "warps", "rois"]
    if volume:
        return standard_args + ["rois"]
    if file_tree:
        return standard_args + ["ref", "bpx_path", "warps", "rois", "seed"]


def get_compulsory_arguments(args):
    """
    Function to return non compulsory
    arguments

    Parameters
    ----------
    args: dict
        command line arguments

    Returns
    -------
    None

    """
    if args["input"]["skip"]:
        return non_compulsory_arguments(skip=True)
    if args["pre_process"]["file_tree"]:
        return non_compulsory_arguments(file_tree=True)
    try:
        if [seed for seed in args["input"]["seed"] if "nii" in seed]:
            return non_compulsory_arguments(volume=True)
    except TypeError:
        error_and_exit(False, "Seeds not provided. Please define with --seed")
    return non_compulsory_arguments(standard=True)


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

    non_complusory = get_compulsory_arguments(args)
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
    omatrix_2_paths = [
        os.path.join(out_dir_name, "nfact_pp", os.path.basename(file), "omatrix2\n")
        for file in files
    ]
    omatrix_2_paths.sort()

    write_to_file(
        nfact_tmp_location,
        "nfact_decomp_sub_list",
        omatrix_2_paths,
        text_is_list=True,
    )


def compulsory_args_for_config(args: dict):
    """
    Function to check for required
    arguments in nfact config file

    Parameters
    ----------
    args: dict
       arguments for NFACT

    Returns
    ------
    None
    """

    if ("Required" in args["global_input"]["seed"][0]) and (
        not args["nfact_pp"]["file_tree"]
    ):
        error_and_exit(False, "config file either needs seeds or file_tree argument")
    if args["nfact_pp"]["file_tree"]:
        args["global_input"]["seed"] = []
    [
        error_and_exit(False, f"{key} not given in config file. Please provide")
        for _, sub_dict in args.items()
        for key, value in sub_dict.items()
        if value == "Required"
    ]


def assign_nfactpp_in_place(args: dict) -> None:
    """
    Function to assign arguments in
    place for nfact_pp

    Parameters
    ----------
    args: dict
        dict of command line arguments

    Returns
    -------
    None
    """
    args["nfact_pp"]["seed"] = args["global_input"]["seed"]
    args["nfact_pp"]["list_of_subjects"] = args["global_input"]["list_of_subjects"]
    args["nfact_pp"]["overwrite"] = args["global_input"]["overwrite"]


def assign_outdir_in_place(args: dict) -> None:
    """
    Function to assign outputdir in
    place for nfact modules

    Parameters
    ----------
    args: dict
        dict of command line arguments

    Returns
    -------
    None
    """
    for module in ["nfact_pp", "nfact_decomp", "nfact_dr"]:
        args[module]["outdir"] = os.path.join(args["global_input"]["outdir"], "nfact")


def assign_nfact_decomp_in_place(args: dict) -> None:
    """
    Function to assign outputdir in
    place for nfact_dr

    Parameters
    ----------
    args: dict
        dict of command line arguments

    Returns
    -------
    None
    """

    args["nfact_decomp"]["overwrite"] = args["global_input"]["overwrite"]


def assign_nfact_dr_in_place(args: dict) -> None:
    """
    Function to assign outputdir in
    place for nfact_dr

    Parameters
    ----------
    args: dict
        dict of command line arguments

    Returns
    -------
    None
    """
    args["nfact_dr"]["nfact_decomp_dir"] = os.path.join(
        args["global_input"]["outdir"], "nfact", "nfact_decomp"
    )
    args["nfact_dr"]["algo"] = args["nfact_decomp"]["algo"]


def medial_wall_file(args: dict) -> None:
    """
    Function to assign medial wall in
    place for nfact_ecomp/nfact_dr

    Parameters
    ----------
    args: dict
        dict of command line arguments

    Returns
    -------
    None
    """
    if args["nfact_pp"]["medial_wall"] or args["nfact_pp"]["file_tree"]:
        path = os.path.join(
            args["global_input"]["outdir"], "nfact", "nfact_pp", "mw_for_decomp.txt"
        )
        args["nfact_decomp"]["medial_wall"] = path
        args["nfact_dr"]["medial_wall"] = path
    if args["nfact_decomp"]["medial_wall"]:
        args["nfact_dr"]["medial_wall"] = args["nfact_decomp"]["medial_wall"]


def update_nfact_args_in_place(args: dict) -> None:
    """
    Function to update arguments
    in place for nfact modules.

    Parameters
    ----------
    args: dict
        dict of command line arguments

    Returns
    -------
    None
    """
    assign_outdir_in_place(args)
    assign_nfactpp_in_place(args)
    assign_nfact_dr_in_place(args)
    assign_nfact_decomp_in_place(args)
