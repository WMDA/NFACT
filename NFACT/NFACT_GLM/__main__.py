from NFACT.NFACT_GLM.nfact_glm_args import nfact_glm_args
import os
import numpy as np
from fsl.data.vest import loadVestFile


def nfact_glm_main() -> None:
    args = nfact_glm_args()
    print(args)
    exit(0)

    glm_data = {
        "dualreg_on_G": [],
        "dualreg_on_W": [],
    }  # stores data for glm if user wants to run that

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
                            save_grey_matter_components(
                                X[con],
                                args["ptxdir"][0],
                                os.path.join(out_glm, f"{y}_{stat}{con+1}"),
                                seeds=seeds,
                            )
                        elif y == "W":
                            save_white_matter(
                                X[con].T,
                                args["ptxdir"][0],
                                os.path.join(out_glm, f"{y}_{stat}{con+1}"),
                            )


if __name__ == "__main__":
    nfact_glm_main()
