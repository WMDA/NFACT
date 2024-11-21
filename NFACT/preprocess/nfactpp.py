# NFACT functions
from .nfactpp_setup import (
    check_seeds_surfaces,
    nfact_pp_folder_setup,
    check_roi_seed_len,
    load_file_tree,
)
from .nfactpp_functions import (
    get_file,
    filetree_get_files,
    process_filetree_args,
    rename_seed,
    stop_masks,
)
from .probtrackx_functions import (
    build_probtrackx2_arguments,
    write_options_to_file,
    Probtrackx,
    get_target2,
    seeds_to_gifti,
)
from NFACT.base.utils import colours, error_and_exit
import os
import shutil


def setup_subject_directory(nfactpp_diretory: str, seed: list) -> None:
    """
    Function to set up the subjects
    directory

    Parameters
    ----------
    nfactpp_diretory: str
        nfactpp_diretory path
    seed: list
        list of seeds

    Returns
    -------
    None
    """
    nfact_pp_folder_setup(nfactpp_diretory)
    for seed_location in seed:
        shutil.copyfile(
            seed_location,
            os.path.join(nfactpp_diretory, "files", os.path.basename(seed_location)),
        )


def process_surface(nfactpp_diretory: str, seed: list, roi: list) -> str:
    """
    Function to process surface seeds

    Parameters
    ----------
    nfactpp_diretory: str
        nfact_pp path
    seed: list
        list of seeds
    roi: list
        list of rois

    Returns
    -------
    str: str
        string of seeds names
    """
    seed_names = rename_seed(seed)
    for img in range(0, len(roi)):
        seeds_to_gifti(
            seed[img],
            roi[img],
            os.path.join(nfactpp_diretory, "files", f"{seed_names[img]}.surf.gii"),
        )
    asc_seeds = [
        os.path.join(nfactpp_diretory, "files", f"{seed}.surf.gii")
        for seed in seed_names
    ]
    return "\n".join(asc_seeds)


def target_generation(arg: dict, nfactpp_diretory: str, col: dict) -> None:
    """
    Function to generate target2 image

    Parameters
    ----------
    arg: dict
        dict of command line arguments
    nfactpp_diretory: str
        str of nfact_pp directory
    col: dict
        dict of colour string

    Returns
    -------
    None
    """
    print(
        f'{col["purple"]}No target given. Creating a whole brain target.{col["reset"]}'
    )
    get_target2(
        arg["ref"],
        os.path.join(nfactpp_diretory, "files", "target2"),
        arg["mm_res"],
        arg["ref"],
        "nearestneighbour",
    )


def process_subject(sub: str, arg: dict, col: dict) -> list:
    """
    Function to process subjects arguments.

    Parameters
    ----------
    sub: str
        path to subjects directory
    arg: dict
        dictionary of command line
        args
    col: dict
        dictionary of colours

    Returns
    -------
    list: list object
        list of subjects arguments
    """

    sub_id = os.path.basename(sub)
    print(f"\n{col['pink']}Setting up:{col['reset']} {sub_id}")

    if arg["file_tree"]:
        arg = process_filetree_args(arg, sub_id)
    seed = get_file(arg["seed"], sub)
    seed_text = "\n".join(seed)
    # using this function not to return a file but check it is an imaging file
    get_file(arg["warps"], sub)
    nfactpp_diretory = os.path.join(arg["outdir"], "nfact_pp", sub_id)
    setup_subject_directory(nfactpp_diretory, seed)

    if arg["surface"]:
        roi = get_file(arg["rois"], sub)
        seed_text = process_surface(roi)

    error_and_exit(write_options_to_file(nfactpp_diretory, seed_text))
    if not arg["target2"]:
        target_generation(arg, nfactpp_diretory, col)

    if arg["stop"]:
        print(f"{col['pink']}Processing:{col['reset']} stop and wtstop files")
        arg = stop_masks(arg, nfactpp_diretory, sub, sub_id)

    return build_probtrackx2_arguments(
        arg,
        sub,
        ptx_options=arg["ptx_options"],
    )


def pre_processing(arg: dict, handler) -> None:
    """
    Main function for nfact PP

    Parameters
    ----------
    arg: dict
       dictionary of command line
       arguments

    Returns
    -------
    None
    """
    col = colours()

    if arg["file_tree"]:
        print(f'{col["plum"]}Filetree {arg["file_tree"].lower()} given {col["reset"]}')
        arg["file_tree"] = load_file_tree(f"{arg['file_tree'].lower()}.tree")

        # load a random subjects seed and ROI to check its type
        arg["seed"] = [filetree_get_files(arg["file_tree"], "sub1", "L", "seed")]

        # Needed for checking if seed is surface
        arg["rois"] = ["filestree"]

    arg["surface"] = check_seeds_surfaces(arg["seed"])

    if arg["surface"]:
        print(f'{col["darker_pink"]}Surface seeds mode{col["reset"]}')
        check_roi_seed_len(arg["seed"], arg["rois"])
    else:
        print(f'{col["darker_pink"]}Volume seed mode{col["reset"]}')

    print(
        f'{col["plum"]}Number of subjects:{col["reset"]} ', len(arg["list_of_subjects"])
    )

    print("\n")
    print("SUBJECT SETUP\n")
    print("-" * 80)
    subjects_commands = [
        process_subject(sub, arg, col) for sub in arg["list_of_subjects"]
    ]

    # This supresses the signit kill message or else it prints it off multiple times for each core
    if arg["n_cores"]:
        handler.set_suppress_messages = True
    print("\n")
    print("TRACTOGRAPHY\n")
    print("-" * 80)
    # Running probtrackx2
    Probtrackx(subjects_commands, arg["n_cores"])
