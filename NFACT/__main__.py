import os
import shutil
import numpy as np
from fsl.data.vest import loadVestFile

from NFACT.utils.utils import Timer, Signit_handler, colours
from NFACT.regression.glm import GLM
from NFACT.regression.dual_regression import dualreg
from NFACT.setup.args import nfact_args
from NFACT.setup.file_setup import create_folder_set_up, get_group_average_files
from NFACT.setup.configure_setup import (
    get_subjects,
    process_seeds,
    list_of_fdt_mat,
    check_config_file,
    load_config_file,
    check_subject_exist,
)
from NFACT.decomposition.decomp import matrix_decomposition, get_parameters
from NFACT.decomposition.matrix_handling import (
    process_fdt_matrix2,
    load_previous_matrix,
    save_avg_matrix,
    load_fdt_matrix,
)
from NFACT.pipes.image_handling import save_W, save_G
from NFACT.pipes.image_handling import winner_takes_all
from NFACT.setup.arg_check import (
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

    if args["config"]:
        args["config"] = load_config_file(args["config"], args["algo"])
        check_config_file(args["config"], args["algo"])

    # Build out folder structure
    if args["overwrite"]:
        if os.path.exists(os.path.join(args["outdir"], "nfact")):
            print(
                f'{col["red"]}Overwrite flag given. {args["outdir"]} directory being overwritten{col["reset"]}'
            )
            shutil.rmtree(os.path.join(args["outdir"], "nfact"), ignore_errors=True)

    create_folder_set_up(args["outdir"])
    get_group_average_files(
        args["ptxdir"][0], os.path.join(args["outdir"], "nfact", "group_averages")
    )
    args["ptx_fdt"] = list_of_fdt_mat(args["ptxdir"])

    # load matrix
    print(f"{col['darker_pink']}\nLoading matrix{col['reset']}")
    matrix_time = Timer()
    matrix_time.tic()

    fdt_2_conn = load_previous_matrix(
        os.path.join(args["outdir"], "nfact", "group_averages", "average_matrix2.npy")
    )

    if fdt_2_conn is None:
        fdt_2_conn = process_fdt_matrix2(
            args["ptx_fdt"], os.path.join(args["outdir"], "nfact"), group_mode
        )
        save_avg_matrix(fdt_2_conn, os.path.join(args["outdir"], "nfact"))
    print(
        f"{col['darker_pink']}loaded matrix in {matrix_time.toc()} secs.{col['reset']}"
    )
    parameters = get_parameters(args["config"], args["algo"], args["dim"])
    # Run the decomposition
    decomposition_timer = Timer()
    decomposition_timer.tic()
    print(f"\nDecomposing fdt matrix using {args['algo'].upper()}")
    components = matrix_decomposition(
        fdt_2_conn,
        algo=args["algo"],
        normalise=args["normalise"],
        sign_flip=args["sign_flip"],
        pca_dim=args["migp"],
        parameters=parameters,
    )
    print(
        f'{col["darker_pink"]}Decomposition took {decomposition_timer.toc()} secs{col["reset"]}'
    )

    # Save the results

    save_W(
        components["white_components"],
        args["ptxdir"][0],
        os.path.join(args["outdir"], f"W_dim{args['dim']}"),
    )
    save_G(
        components["grey_components"],
        args["ptxdir"][0],
        os.path.join(args["outdir"], f"G_dim{args['dim']}"),
        seeds=seeds,
    )

    if args["wta"]:
        # Save winner-takes-all maps
        print("...Saving winner-take-all maps")
        W_wta = winner_takes_all(
            components["white_components"], axis=0, z_thr=args["wta_zthr"]
        )
        G_wta = winner_takes_all(
            components["grey_components"], axis=1, z_thr=args["wta_zthr"]
        )
        save_W(
            W_wta,
            args["ptxdir"][0],
            os.path.join(args["outdir"], f"W_dim{args['dim']}_wta"),
        )
        save_G(
            G_wta,
            args["ptxdir"][0],
            os.path.join(args["outdir"], f"G_dim{args['dim']}_wta"),
            seeds=seeds,
        )

    glm_data = {
        "dualreg_on_G": [],
        "dualreg_on_W": [],
    }  # stores data for glm if user wants to run that
    if group_mode:
        # Only run the dual regression if the user asked for it
        if not args["skip_dual_reg"]:
            print("...Doing dual regression")

            for idx, matfile in enumerate(args["ptx_fdt"]):
                print(f"... subj-{idx} - mat: {matfile}")
                idx3 = str(idx).zfill(3)  # zero-pad index
                Cs = load_fdt_matrix(os.path.join(matfile))

                # dual reg on G
                Gs, Ws = dualreg(Cs, components["grey_components"])
                out_dualreg = os.path.join(
                    args["outdir"], args["algo"].upper(), "dual_reg", "G"
                )
                save_W(
                    Ws,
                    args["ptxdir"][idx],
                    os.path.join(out_dualreg, f"Ws_{idx3}_dim{args['dim']}"),
                )
                save_G(
                    Gs,
                    args["ptxdir"][idx],
                    os.path.join(out_dualreg, f"Gs_{idx3}_dim{args['dim']}"),
                    seeds=seeds,
                )
                # keep data for GLM?
                if args["glm_mat"]:
                    glm_data["dualreg_on_G"].append([Gs, Ws])

                # dual reg on W
                Gs, Ws = dualreg(Cs, components["white_components"])
                out_dualreg = os.path.join(
                    args["outdir"], args["algo"].upper(), "dual_reg", "W"
                )
                save_W(
                    Ws,
                    args["ptxdir"][idx],
                    os.path.join(out_dualreg, f"Ws_{idx3}_dim{args['dim']}"),
                )
                save_G(
                    Gs,
                    args["ptxdir"][idx],
                    os.path.join(out_dualreg, f"Gs_{idx3}_dim{args['dim']}"),
                    seeds=seeds,
                )
                if args["glm_mat"]:
                    glm_data["dualreg_on_W"].append([Gs, Ws])

                # memory management
                del Cs

    # GLM?
    if args["glm_mat"]:
        print("...Running GLMs")
        if not group_mode:
            raise (Exception("Must provide multiple subjects data to run a GLM"))
        if args.mode != "dualreg":
            raise (Exception("Must be in dualreg mode to run a GLM"))
        # Load design files

        desmat = loadVestFile(args["glm_mat"])
        conmat = loadVestFile(args["glm_con"])
        glm = GLM()
        # Loop through dualreg targets
        for dr_target in ["G", "W"]:
            # Loop through dimensions and run GLMs
            print("Warning. NFACT will overwrite previous analysis at the moments")
            out_glm = os.path.join(args["outdir"], "GLM")
            os.mkdir(os.path.join(out_glm, "G"))
            os.mkdir(os.path.join(out_glm, "W"))
            all_stats = {"G": [], "W": []}
            for comp in range(args["dim"]):
                # assemble data matrix subject-by-gm or subject-by-wm
                data = {
                    "G": np.array(
                        [
                            glm_data[f"dualreg_on_{dr_target}"][i][0][:, comp]
                            for i in range(len(args["ptx_fdt"]))
                        ]
                    ),
                    "W": np.array(
                        [
                            glm_data[f"dualreg_on_{dr_target}"][i][1][comp, :]
                            for i in range(len(args["ptx_fdt"]))
                        ]
                    ),
                }
                for y in data:
                    glm.fit(desmat, data[y])
                    stats = glm.calc_stats(conmat)
                    all_stats[y].append(stats)

            # save results
            for stat in ["tstat", "zstat", "pval"]:
                for y in ["G", "W"]:
                    X = np.asarray(
                        [s[stat] for s in all_stats[y]]
                    )  # n_comps x n_contrasts x n_voxels
                    X = np.transpose(X, (1, 2, 0))
                    for con in range(X.shape[0]):
                        if y == "G":
                            save_G(
                                X[con],
                                args["ptxdir"][0],
                                os.path.join(out_glm, f"{y}_{stat}{con+1}"),
                                seeds=seeds,
                            )
                        elif y == "W":
                            save_W(
                                X[con].T,
                                args["ptxdir"][0],
                                os.path.join(out_glm, f"{y}_{stat}{con+1}"),
                            )
    print("---- Done ----")


if __name__ == "__main__":
    nfact_main()
