import os
import numpy as np
from fsl.data.vest import loadVestFile

from NFACT.utils.utils import Timer
from NFACT.regression.glm import GLM
from NFACT.regression.dual_regression import dualreg
from NFACT.setup.args import cmd_args
from NFACT.decomposition.decomp import matrix_decomposition
from NFACT.decomposition.matrix_handling import load_mat2, avg_matrix2
from NFACT.pipes.image_handling import save_W, save_G, is_gifti, is_nifti
from NFACT.pipes.data_pipes import winner_takes_all, get_seed


def main():
    args = cmd_args()

    # Import after parsing argument to speed up printing help message

    out_folder = args["outdir"]
    # Create out_folder if it does not exist already
    if not os.path.isdir(out_folder):
        os.makedirs(out_folder, exist_ok=True)
    # check that I'll be able to save results
    if not os.access(out_folder, os.W_OK):
        raise (Exception(f"Cannot write into {out_folder}. Check permissions..."))

    ptx_folder = args["ptxdir"]

    group_mode = False
    # if len = 1 --> could be text file or single folder
    if len(ptx_folder) == 1:
        if not os.path.isdir(ptx_folder[0]):
            with open(ptx_folder[0], "r") as f:
                ptx_folder = [x.strip() for x in f.read().split(" ")]
    if len(ptx_folder) == 1:
        print("...Single ptx_folder provided")
    else:
        group_mode = True
        print("...List of ptx_folders provided")
    print(ptx_folder)

    # check that I can find the seed files
    seeds = args["seeds"]
    if seeds is None:
        if group_mode:
            raise (Exception("Must provide seeds if running in group mode."))
        seeds = get_seed(ptx_folder[0])
    print(f"...Seed files are: {seeds}")
    for s in seeds:
        if not is_nifti(s) and not is_gifti(s):
            raise (
                Exception(f"Seed file {s} does not appear to be a valid GIFTI or NIFTI")
            )

    # Load the matrix
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
            os.makedirs(os.path.join(out_folder, "dualreg_on_G"), exist_ok=True)
            os.makedirs(os.path.join(out_folder, "dualreg_on_W"), exist_ok=True)
            for idx, matfile in enumerate(list_of_matrices):
                print(f"... subj-{idx} - mat: {matfile}")
                idx3 = str(idx).zfill(3)  # zero-pad index
                Cs = load_mat2(os.path.join(matfile))

                # dual reg on G
                Gs, Ws = dualreg(Cs, G)
                out_dualreg = os.path.join(out_folder, "dualreg_on_G")
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
                out_dualreg = os.path.join(out_folder, "dualreg_on_W")
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
            out_glm = os.path.join(out_folder, f"glm_on_{dr_target}")
            os.makedirs(out_glm, exist_ok=True)
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
    main()
