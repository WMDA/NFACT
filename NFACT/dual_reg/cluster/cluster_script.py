from NFACT.dual_reg.nfact_dr_functions import get_group_level_components
from NFACT.base.matrix_handling import load_fdt_matrix
from NFACT.dual_reg.dual_regression import (
    nmf_dual_regression,
    ica_dual_regression,
    run_decomp,
)
from NFACT.dual_reg.nfact_dr_functions import save_dual_regression_images
import argparse
import os


def script_args() -> dict:
    """
    Script args

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary
        dict of cmd options
    """
    parser = argparse.ArgumentParser(description="Run Dual Regression")
    parser.add_argument(
        "--fdt_path", required=True, help="Directory to individual subject fdt path"
    )
    parser.add_argument(
        "--output_dir", required=True, help="Directory to save the output components."
    )
    parser.add_argument(
        "--component_path", required=True, help="Directory to components path."
    )
    parser.add_argument(
        "--group_average_path", required=True, help="Path to group averages."
    )
    parser.add_argument("--algo", required=True, help="Which algo has been run")
    parser.add_argument("--seeds", required=True, nargs="+", help="Path to seed(s).")
    parser.add_argument("--id", required=True, help="Subject ID.")
    parser.add_argument(
        "--medial_wall", nargs="+", default=False, help="Path to medial wall(s)."
    )
    parser.add_argument(
        "--parallel", default=1, type=int, help="Number of cores to parallel with"
    )
    return vars(parser.parse_args())


def main_dr(args: dict) -> None:
    """
    Main NMF function.

    Parameters
    ----------
    args: dict
        dictionary of args

    Returns
    -------
    None
    """
    try:
        print("Number of cores: ", args["parallel"])
        print("Obtaining Group Level Components")
        components = get_group_level_components(
            args["component_path"],
            args["group_average_path"],
            args["seeds"],
            args["medial_wall"],
        )
    except Exception as e:
        print("Failed to obtain components due to ", e)
        exit(1)
    try:
        print("Obtaining FDT Matrix")
        matrix = load_fdt_matrix(args["fdt_path"])
        dr_regression = nmf_dual_regression if args["algo"] else ica_dual_regression
        print("Running Dual Regression")
        dr_results = run_decomp(dr_regression, components, matrix, args["parallel"])
        print("Saving Components")
        save_dual_regression_images(
            dr_results,
            args["output_dir"],
            args["seeds"],
            args["algo"].upper(),
            dr_results["white_components"].shape[0],
            args["id"],
            os.path.dirname(args["fdt_path"]),
            args["medial_wall"],
        )
    except Exception as e:
        print(e)
    return None


if __name__ == "__main__":
    args = script_args()
    main_dr(args)
