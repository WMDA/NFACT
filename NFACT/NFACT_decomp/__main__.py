import os
import shutil

from NFACT.utils.utils import Timer, Signit_handler, colours
from NFACT.NFACT_decomp.regression.dual_regression import Dual_regression
from NFACT.NFACT_decomp.setup.args import nfact_args
from NFACT.NFACT_decomp.setup.file_setup import (
    create_folder_set_up,
    get_group_average_files,
)
from NFACT.NFACT_decomp.setup.configure_setup import (
    get_subjects,
    process_seeds,
    check_config_file,
    load_config_file,
    check_subject_exist,
    seed_type,
)
from NFACT.NFACT_decomp.decomposition.decomp import matrix_decomposition, get_parameters
from NFACT.NFACT_decomp.decomposition.matrix_handling import (
    process_fdt_matrix2,
    load_previous_matrix,
    save_avg_matrix,
)
from NFACT.NFACT_decomp.pipes.image_handling import save_images
from NFACT.NFACT_decomp.pipes.image_handling import winner_takes_all
from NFACT.NFACT_decomp.setup.arg_check import (
    check_complusory_arguments,
    check_algo,
    process_command_args,
)


def nfact_main() -> None:
    """
    Main nfact function

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Setting up nfact
    handler = Signit_handler()
    args = nfact_args()
    col = colours()

    # Do argument checking
    check_complusory_arguments(args)
    args["algo"] = check_algo(args["algo"])
    args = process_command_args(args)

    # check subjects exist
    args = get_subjects(args)
    check_subject_exist(args["ptxdir"])
    print("Number of Subjects:", len(args["ptxdir"]), "\n")

    group_mode = True if len(args["ptxdir"]) > 0 else False

    # process seeds
    seeds = process_seeds(args["seeds"])
    img_type = seed_type(seeds)

    if args["config"]:
        args["config"] = load_config_file(args["config"], args["algo"])
        check_config_file(args["config"], args["algo"])

    # Build out folder structure
    if args["overwrite"]:
        if os.path.exists(os.path.join(args["outdir"], "nfact")):
            print(
                f'{col["red"]}Overwrite flag given. {args["outdir"]} directory being overwritten{col["reset"]}\n'
            )
            shutil.rmtree(os.path.join(args["outdir"], "nfact"), ignore_errors=True)

    create_folder_set_up(args["outdir"])
    get_group_average_files(
        args["ptxdir"][0], os.path.join(args["outdir"], "nfact", "group_averages")
    )

    # load matrix
    print(f"{col['darker_pink']}\nLoading matrix{col['reset']}\n")
    matrix_time = Timer()
    matrix_time.tic()

    fdt_2_conn = load_previous_matrix(
        os.path.join(args["outdir"], "nfact", "group_averages", "average_matrix2.npy")
    )

    if fdt_2_conn is None:
        fdt_2_conn = process_fdt_matrix2(args["ptxdir"], group_mode)
        save_avg_matrix(fdt_2_conn, os.path.join(args["outdir"], "nfact"))
    print(
        f"{col['darker_pink']}loaded matrix in {matrix_time.toc()} secs.{col['reset']}\n"
    )

    # Get hyperparameters
    parameters = get_parameters(args["config"], args["algo"], args["dim"])

    # Run the decomposition
    decomposition_timer = Timer()
    decomposition_timer.tic()
    print(f"Decomposing fdt matrix using {args['algo'].upper()}")
    components = matrix_decomposition(
        fdt_2_conn,
        algo=args["algo"],
        normalise=args["normalise"],
        signflip=args["sign_flip"],
        pca_dim=args["migp"],
        parameters=parameters,
    )
    print(
        f'{col["darker_pink"]}Decomposition took {decomposition_timer.toc()} secs{col["reset"]}\n'
    )

    # Save the results
    save_images(
        img_type,
        components,
        os.path.join(
            args["outdir"],
            "nfact",
        ),
        seeds,
        args["algo"].upper(),
        args["dim"],
    )

    if args["wta"]:
        # Save winner-takes-all maps
        print("Saving winner-take-all maps\n")
        winner_takes_all(
            components,
            args["wta_zthr"],
            args["algo"].upper(),
            os.path.join(
                args["outdir"],
                "nfact",
            ),
            img_type,
            seeds,
            args["dim"],
        )

    if group_mode and not args["skip_dual_reg"]:
        print(
            f"{col['plum']}Performing dual regression on {len(args['ptxdir'])} subjects{col['reset']}"
        )
        dual_reg = Dual_regression(
            algo=args["algo"],
            normalise=args["normalise"],
            parallel=False,
            list_of_files=args["ptxdir"],
            component=components,
            save_type=img_type,
            seeds=seeds,
            nfact_directory=os.path.join(
                args["outdir"],
                "nfact",
            ),
        )
        dual_reg.run()
    print(f"\n{col['darker_pink']}NFACT has finished{col['reset']}")
    exit(0)


if __name__ == "__main__":
    nfact_main()