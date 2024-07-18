import os
import shutil
import numpy as np
from fsl.data.vest import loadVestFile

from NFACT.utils.utils import Timer, Signit_handler, colours
from NFACT.regression.glm import GLM
from NFACT.regression.dual_regression import dualreg
from NFACT.setup.args import nfact_args
from NFACT.setup.setup import (
    get_subjects,
    check_subject_exist,
    process_seeds,
    create_folder_set_up,
)
from NFACT.decomposition.decomp import matrix_decomposition
from NFACT.decomposition.matrix_handling import load_mat2, avg_matrix2
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
    handler = Signit_handler()
    args = nfact_args()

    # Do argument checking
    check_complusory_arguments(args)
    args["algo"] = check_algo(args["algo"])
    args = process_command_args(args)

    # put here if ptx_folder or list of subjects
    args = get_subjects(args)
    check_subject_exist(args["ptxdir"])

    ptx_folder = args["ptxdir"]
    # error check that participants exist
    out_folder = args["outdir"]

    # set up output dir here

    group_mode = True if len(ptx_folder) > 0 else False

    # find seeds
    seeds = process_seeds(args["seeds"])
    # remove for checking extensions

    # Build out folder structure
    if args["overwrite"]:
        breakpoint()
        if os.path.exists(os.path.join(args["outdir"], "nfact")):
            col = colours()
            print(
                f'{col["red"]}Overwrite flag given. {args["outdir"]} directory being overwritten{col["reset"]}'
            )
            shutil.rmtree(os.path.join(args["outdir"], "nfact"), ignore_errors=True)

    create_folder_set_up(args["outdir"])
    print("Number of Subjects:", len(ptx_folder))

    # Load the matrix and save. TODO: make nfact look for previous matrix
    if group_mode:
        # Calculate the group average matrix
        list_of_matrices = [os.path.join(f, "fdt_matrix2.dot") for f in ptx_folder]
        print("... Averaging subject matrices")
        t = Timer()
        t.tic()
        C = avg_matrix2(list_of_matrices)
    else:
        # Load a single matrix
        C = load_mat2(os.path.join(ptx_folder[0], "fdt_matrix2.dot"))

    print(f"...loaded matricies in {t.toc()} secs.")

    # Run the decomposition
    n_comps = args["dim"]
    kwargs = {
        "do_migp": args["migp"] > 0,
        "d_pca": args["migp"],
        "n_dim": args["migp"],
        "algo": args["algo"],
        "normalise": args["normalise"],
        "sign_flip": args["sign_flip"],
    }

    # Run the decomposition
    G, W = matrix_decomposition(C, n_components=n_comps, **kwargs)

    # Save the results
    # If group mode, save average then run dualreg to save the individual stuff (if user requested)
    if group_mode:
        print("...Saving group average results")
    else:
        print("...Saving group decomposition results")
    save_W(W, ptx_folder[0], os.path.join(out_folder, f"W_dim{n_comps}"))
    save_G(G, ptx_folder[0], os.path.join(out_folder, f"G_dim{n_comps}"), seeds=seeds)

    if args["wta"]:
        # Save winner-takes-all maps
        print("...Saving winner-take-all maps")
        W_wta = winner_takes_all(W, axis=0, z_thr=args["wta_zthr"])
        G_wta = winner_takes_all(G, axis=1, z_thr=args["wta_zthr"])
        save_W(W_wta, ptx_folder[0], os.path.join(out_folder, f"W_dim{n_comps}_wta"))
        save_G(
            G_wta,
            ptx_folder[0],
            os.path.join(out_folder, f"G_dim{n_comps}_wta"),
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

            for idx, matfile in enumerate(list_of_matrices):
                print(f"... subj-{idx} - mat: {matfile}")
                idx3 = str(idx).zfill(3)  # zero-pad index
                Cs = load_mat2(os.path.join(matfile))

                # dual reg on G
                Gs, Ws = dualreg(Cs, G)
                out_dualreg = os.path.join(
                    out_folder, args["algo"].upper(), "dual_reg", "G"
                )
                save_W(
                    Ws,
                    ptx_folder[idx],
                    os.path.join(out_dualreg, f"Ws_{idx3}_dim{n_comps}"),
                )
                save_G(
                    Gs,
                    ptx_folder[idx],
                    os.path.join(out_dualreg, f"Gs_{idx3}_dim{n_comps}"),
                    seeds=seeds,
                )
                # keep data for GLM?
                if args["glm_mat"]:
                    glm_data["dualreg_on_G"].append([Gs, Ws])

                # dual reg on W
                Gs, Ws = dualreg(Cs, W)
                out_dualreg = os.path.join(
                    out_folder, args["algo"].upper(), "dual_reg", "W"
                )
                save_W(
                    Ws,
                    ptx_folder[idx],
                    os.path.join(out_dualreg, f"Ws_{idx3}_dim{n_comps}"),
                )
                save_G(
                    Gs,
                    ptx_folder[idx],
                    os.path.join(out_dualreg, f"Gs_{idx3}_dim{n_comps}"),
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
            out_glm = os.path.join(out_folder, "GLM")
            os.mkdir(os.path.join(out_glm, "G"))
            os.mkdir(os.path.join(out_glm, "W"))
            all_stats = {"G": [], "W": []}
            for comp in range(n_comps):
                # assemble data matrix subject-by-gm or subject-by-wm
                data = {
                    "G": np.array(
                        [
                            glm_data[f"dualreg_on_{dr_target}"][i][0][:, comp]
                            for i in range(len(list_of_matrices))
                        ]
                    ),
                    "W": np.array(
                        [
                            glm_data[f"dualreg_on_{dr_target}"][i][1][comp, :]
                            for i in range(len(list_of_matrices))
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
                                ptx_folder[0],
                                os.path.join(out_glm, f"{y}_{stat}{con+1}"),
                                seeds=seeds,
                            )
                        elif y == "W":
                            save_W(
                                X[con].T,
                                ptx_folder[0],
                                os.path.join(out_glm, f"{y}_{stat}{con+1}"),
                            )
    print("---- Done ----")


if __name__ == "__main__":
    nfact_main()
