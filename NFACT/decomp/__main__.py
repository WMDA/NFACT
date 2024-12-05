from NFACT.base.logging import NFACT_logs
from NFACT.base.utils import Timer, colours, nprint
from NFACT.base.signithandler import Signit_handler
from NFACT.base.setup import (
    check_subject_exist,
    check_algo,
    get_subjects,
    process_input_imgs,
    check_arguments,
    check_seeds_surfaces,
)

from .setup.args import nfact_decomp_args, nfact_decomp_splash
from .setup.file_setup import (
    create_folder_set_up,
    get_group_average_files,
)
from .setup.configure_setup import (
    check_config_file,
    load_config_file,
)
from .decomposition.decomp import matrix_decomposition, get_parameters
from .decomposition.matrix_handling import (
    process_fdt_matrix2,
    load_previous_matrix,
    save_avg_matrix,
)

from .pipes.image_handling import winner_takes_all, save_images
from .setup.arg_check import process_command_args
import os
import shutil


def nfact_decomp_main(args: dict = None) -> None:
    """
    Main nfact function

    Parameters
    ----------
    arg: dict
        Set of command line arguments
        from nfact_pipeline
        Default is None

    Returns
    -------
    None
    """
    # Setting up nfact

    Signit_handler()
    to_exit = False
    if not args:
        args = nfact_decomp_args()
        to_exit = True
    col = colours()

    # Do argument checking
    check_arguments(args, ["list_of_subjects", "dim", "seeds", "outdir"])
    args["algo"] = check_algo(args["algo"])
    args = process_command_args(args)

    # check subjects exist
    args = get_subjects(args)
    check_subject_exist(args["ptxdir"])
    print(f"{col['plum']}Number of Subjects:{col['reset']}", len(args["ptxdir"]))

    group_mode = True if len(args["ptxdir"]) > 0 else False

    # process seeds
    args["seeds"] = process_input_imgs(args["seeds"])
    args["surface"] = check_seeds_surfaces(args["seeds"])
    if args["surface"] and args["medial_wall"]:
        args["medial_wall"] = process_input_imgs(args["medial_wall"])
    else:
        args["medial_wall"] = False
    if args["config"]:
        args["config"] = load_config_file(args["config"], args["algo"])
        check_config_file(args["config"], args["algo"])

    # Build out folder structure
    if args["overwrite"]:
        if os.path.exists(os.path.join(args["outdir"], "nfact_decomp")):
            print(
                f'{col["red"]}Overwrite flag given. {args["outdir"]}/nfact_decomp directory being overwritten{col["reset"]}\n'
            )
            shutil.rmtree(
                os.path.join(args["outdir"], "nfact_decomp"), ignore_errors=True
            )

    create_folder_set_up(args["outdir"])
    print(f"{col['plum']}NFACT folder:{col['reset']} {args['outdir']}")

    # Get hyperparameters
    parameters = get_parameters(args["config"], args["algo"], args["dim"])

    # Set up log
    log = NFACT_logs(args["algo"], "decomp", len(args["ptxdir"]))
    log.set_up_logging(os.path.join(args["outdir"], "nfact_decomp", "logs"))
    log.inital_log(nfact_decomp_splash())
    log.log_break("input")
    log.log_arguments(args)
    log.log_parameters(parameters)
    log.log_break("nfact decomp workflow")
    print(
        f'{col["plum"]}Log file:{col["reset"]} {os.path.join(args["outdir"], "nfact_decomp", "logs")}'
    )

    get_group_average_files(
        args["ptxdir"][0],
        os.path.join(args["outdir"], "nfact_decomp", "group_averages"),
    )

    # load matrix
    nprint("\nLOADING MATRIX")
    nprint("-" * 100)
    matrix_time = Timer()
    matrix_time.tic()

    fdt_2_conn = load_previous_matrix(
        os.path.join(
            args["outdir"], "nfact_decomp", "group_averages", "average_matrix2.npy"
        )
    )
    print_str = "Loading previously saved" if fdt_2_conn is not None else "Averaging"
    nprint(f"{col['pink']}NFACT Matrix:{col['reset']} {print_str}")
    if fdt_2_conn is None:
        save_directory = os.path.join(args["outdir"], "nfact_decomp", "group_averages")
        fdt_2_conn = process_fdt_matrix2(args["ptxdir"], group_mode)
        save_avg_matrix(fdt_2_conn, save_directory)
        nprint(f'{col["pink"]}Saving Matrix:{col["reset"]} {save_directory}')
    nprint(
        f"{col['pink']}Matrix Loading Time:{col['reset']} {matrix_time.how_long()} \n"
    )

    # Run the decomposition
    decomposition_timer = Timer()
    decomposition_timer.tic()

    nprint("DECOMPOSING MATRIX")
    nprint("-" * 100)
    nprint(f"{col['pink']}NFACT method:{col['reset']} {args['algo'].upper()}")

    components = matrix_decomposition(
        fdt_2_conn,
        algo=args["algo"],
        normalise=args["normalise"],
        signflip=args["sign_flip"],
        pca_dim=args["components"],
        parameters=parameters,
        pca_type=args["pca_type"],
    )
    nprint(
        f'{col["pink"]}Decomposition time:{col["reset"]} {decomposition_timer.how_long()}\n'
    )

    # Save the results
    save_images(
        components,
        os.path.join(
            args["outdir"],
            "nfact_decomp",
        ),
        args["seeds"],
        args["algo"].upper(),
        args["dim"],
        args["medial_wall"],
    )

    if args["wta"]:
        # Save winner-takes-all maps
        nprint("Saving winner-take-all maps\n")
        winner_takes_all(
            components,
            args["wta_zthr"],
            args["algo"].upper(),
            os.path.join(
                args["outdir"],
                "nfact_decomp",
            ),
            args["seeds"],
            args["dim"],
            args["medial_wall"],
        )
    nprint(f"{col['darker_pink']}NFACT decomp has finished{col['reset']}")

    log.clear_logging()

    if to_exit:
        exit(0)


if __name__ == "__main__":
    nfact_decomp_main()
    exit(0)
