from .nfact_glm_args import nfact_glm_args
from .nfact_glm_setup import check_compulsory_arguments
import os
import numpy as np
from fsl.data.vest import loadVestFile
from NFACT.NFACT_base.setup import check_algo


def nfact_glm_main() -> None:
    """
    Main Function for NFACT GLM.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    args = nfact_glm_args()
    args["type_of_decomp"] = check_algo(args["type_of_decomp"])
    args["analysis_name"] = (
        args["type_of_decomp"].upper() + "_GLM"
        if not args["analysis_name"]
        else args["analysis_name"]
    )

    check_compulsory_arguments(args)

    exit(0)


#    glm_data = {
#        "dualreg_on_G": [],
#        "dualreg_on_W": [],
#    }
#
#    desmat = loadVestFile(args["design_matrix"])
#    conmat = loadVestFile(args["constrast"])
#    glm = GLM()
#    # Loop through dualreg targets
#    for dr_target in ["G", "W"]:
#        # Loop through dimensions and run GLMs
#        print("Warning. NFACT will overwrite previous analysis at the moments")
#        out_glm = os.path.join(args["outdir"], "GLM")
#        os.mkdir(os.path.join(out_glm, "G"))
#        os.mkdir(os.path.join(out_glm, "W"))
#        all_stats = {"G": [], "W": []}
#        for comp in range(args["dim"]):
#            # assemble data matrix subject-by-gm or subject-by-wm
#            data = {
#                "G": np.array(
#                    [
#                        glm_data[f"dualreg_on_{dr_target}"][i][0][:, comp]
#                        for i in range(len(args["ptx_fdt"]))
#                    ]
#                ),
#                "W": np.array(
#                    [
#                        glm_data[f"dualreg_on_{dr_target}"][i][1][comp, :]
#                        for i in range(len(args["ptx_fdt"]))
#                    ]
#                ),
#            }
#            for y in data:
#                glm.fit(desmat, data[y])
#                stats = glm.calc_stats(conmat)
#                all_stats[y].append(stats)
#        # save results
#        for stat in ["tstat", "zstat", "pval"]:
#            for y in ["G", "W"]:
#                X = np.asarray(
#                    [s[stat] for s in all_stats[y]]
#                )  # n_comps x n_contrasts x n_voxels
#                X = np.transpose(X, (1, 2, 0))
#                for con in range(X.shape[0]):
#                    if y == "G":
#                        save_grey_matter_components(
#                            X[con],
#                            args["ptxdir"][0],
#                            os.path.join(out_glm, f"{y}_{stat}{con+1}"),
#                            seeds=seeds,
#                        )
#                    elif y == "W":
#                        save_white_matter(
#                            X[con].T,
#                            args["ptxdir"][0],
#                            os.path.join(out_glm, f"{y}_{stat}{con+1}"),
#                        )
#
#
if __name__ == "__main__":
    nfact_glm_main()
