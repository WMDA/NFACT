import os
import re
import shutil

# NFACT functions
from NFACT.NFACT_base.imagehandling import get_file
from NFACT.NFACT_base.utils import colours, error_and_exit
from .nfactpp_setup import check_surface_arguments, nfact_pp_folder_setup
from .nfactpp_functions import (
    hcp_get_seeds,
    hcp_get_rois,
    hcp_reorder_seeds_rois,
    update_seeds_file,
)
from .probtrackx_functions import (
    build_probtrackx2_arguments,
    write_options_to_file,
    Probtrackx,
    get_target2,
    seeds_to_ascii,
)


def surf_volume_main(arg: dict, handler) -> None:
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

    surface_processing = check_surface_arguments(arg["seed"], arg["rois"])
    col = colours()

    if surface_processing:
        print(f'{col["darker_pink"]}Surface seeds mode{col["reset"]}')
    else:
        print(f'{col["darker_pink"]}Volume seed mode{col["reset"]}')

    print("Number of subjects: ", len(arg["list_of_subjects"]))
    subjects_commands = []

    for sub in arg["list_of_subjects"]:
        # looping over subjects and building out directories
        print(f"\n{col['pink']}Setting up:{col['reset']} {os.path.basename(sub)}")
        seed = get_file(arg["seed"], sub)
        seed_text = "\n".join(seed)
        # using this function not to return a file but check it is an imaging file
        get_file(arg["warps"], sub)

        nfactpp_diretory = os.path.join(
            arg["outdir"], "nfact_pp", os.path.basename(sub)
        )

        if arg["overwrite"]:
            if os.path.exists(nfactpp_diretory):
                print(
                    f'{col["red"]}{arg["outdir"]} directory already exists. Overwriting{col["reset"]}'
                )
                shutil.rmtree(nfactpp_diretory, ignore_errors=True)

        nfact_pp_folder_setup(nfactpp_diretory)

        [
            shutil.copyfile(
                seed_location,
                os.path.join(
                    nfactpp_diretory, "files", os.path.basename(seed_location)
                ),
            )
            for seed_location in seed
        ]

        if surface_processing:
            roi = get_file(arg["rois"], sub)
            seed_names = [
                re.sub(r"..ii", "", os.path.basename(seeds)) for seeds in seed
            ]
            for img in range(0, len(roi)):
                seeds_to_ascii(
                    seed[img],
                    roi[img],
                    os.path.join(nfactpp_diretory, "files", f"{seed_names[img]}.asc"),
                )
            asc_seeds = [
                os.path.join(nfactpp_diretory, "files", f"{seed}.asc")
                for seed in seed_names
            ]
            seed_text = "\n".join(asc_seeds)

        error_and_exit(write_options_to_file(nfactpp_diretory, seed_text))

        if not arg["target2"]:
            print(
                f'{col["purple"]}No target given. Creating a whole brain target.{col["reset"]}'
            )
            get_target2(
                arg["ref"],
                os.path.join(nfactpp_diretory, "files", "target2"),
                arg["res"],
                arg["ref"],
                "nearestneighbour",
            )

        subjects_commands.append(
            build_probtrackx2_arguments(
                arg,
                sub,
                hcp_stream=False,
                ptx_options=arg["ptx_options"],
            )
        )

    # This supresses the signit kill message or else it prints it off multiple times for each core
    if arg["n_cores"]:
        handler.set_suppress_messages = True

    # Running probtrackx2
    Probtrackx(subjects_commands, arg["cluster"], arg["n_cores"], arg["dont_log"])
    if surface_processing:
        [
            update_seeds_file(os.path.join(sub, arg["outdir"], "seeds.txt"))
            for sub in arg["list_of_subjects"]
        ]


def hcp_stream_main(arg: dict, handler: object) -> None:
    """
    hcp stream main function

    Parameters
    ----------
    arg: dict
       dictionary of command line
       arguments

    Returns
    ------
    None

    """
    col = colours()
    print(f'{col["darker_pink"]}HCP stream selected{col["reset"]}')
    subjects_commands = []
    print("Number of subjects: ", len(arg["list_of_subjects"]))
    for sub in arg["list_of_subjects"]:
        # looping over subjects and building out directories
        print(f"\n{col['pink']}Setting up:{col['reset']} {os.path.basename(sub)}")
        seeds = hcp_get_seeds(sub)
        arg["rois"] = hcp_get_rois(sub)
        nfactpp_diretory = os.path.join(sub, arg["outdir"])

        if arg["overwrite"]:
            if os.path.exists(nfactpp_diretory):
                print(
                    f'{col["red"]}{arg["outdir"]} directory already exists. Overwriting{col["reset"]}'
                )
                shutil.rmtree(nfactpp_diretory, ignore_errors=True)

        nfact_pp_folder_setup(nfactpp_diretory)

        ordered_by_hemisphere = hcp_reorder_seeds_rois(seeds, arg["rois"])
        for hemishphere, img in ordered_by_hemisphere.items():
            seeds_to_ascii(
                img[0],
                img[1],
                os.path.join(
                    nfactpp_diretory, "files", f"{hemishphere}_white.32k_fs_LR.surf.asc"
                ),
            )

        asc_seeds = [
            os.path.join(nfactpp_diretory, "files", "left_white.32k_fs_LR.surf.asc"),
            os.path.join(nfactpp_diretory, "files", "right_white.32k_fs_LR.surf.asc"),
        ]
        seed_text = "\n".join(asc_seeds)
        error_and_exit(write_options_to_file(nfactpp_diretory, seed_text))

        if not arg["target2"]:
            print(
                f'{col["purple"]}No target given. Creating a whole brain target.{col["reset"]}'
            )

            get_target2(
                arg["ref"],
                os.path.join(nfactpp_diretory, "files", "target2"),
                arg["res"],
                arg["ref"],
                "nearestneighbour",
            )
        subjects_commands.append(build_probtrackx2_arguments(arg, sub, hcp_stream=True))

    if arg["n_cores"]:
        handler.set_suppress_messages = True

    Probtrackx(subjects_commands, arg["cluster"], arg["n_cores"])
    [
        update_seeds_file(os.path.join(sub, arg["outdir"], "seeds.txt"))
        for sub in arg["list_of_subjects"]
    ]
