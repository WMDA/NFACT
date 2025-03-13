from NFACT.dual_reg.nfact_dr_functions import get_group_level_components
from NFACT.base.matrix_handling import load_fdt_matrix
from NFACT.dual_reg.dual_regression import (
    nmf_dual_regression,
    ica_dual_regression,
    run_decomp,
)
from NFACT.dual_reg.nfact_dr_functions import save_dual_regression_images
from NFACT.base.utils import colours, error_and_exit, nprint
import argparse
import os


def cluster_mode_args() -> dict:
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
    parser.add_argument("--roi", nargs="+", default=False, help="Path to roi(s).")
    parser.add_argument(
        "--parallel", default=1, type=int, help="Number of cores to parallel with"
    )
    return vars(parser.parse_args())


def dual_regression_pipeline(args: dict) -> None:
    """
    The dual regression pipeline function.
    This function either runs the pipeline
    locally or as an individual script to
    the cluster.

    Parameters
    ----------
    args: dict
        dictionary of args

    Returns
    -------
    None
    """
    col = colours()
    nprint(
        f"{col['plum']}Number of cores{col['reset']}: ",
        args["parallel"],
        to_flush=True,
    )
    nprint("-" * 100)
    nprint(
        f"{col['pink']}Obtaining{col['reset']}: Group Level Components", to_flush=True
    )

    try:
        components = get_group_level_components(
            args["component_path"],
            args["group_average_path"],
            args["seeds"],
            args["roi"],
        )
    except Exception:
        error_and_exit(False, "Unable to find components")

    nprint(f"{col['plum']}Subject ID{col['reset']}: {args['id']}", to_flush=True)
    nprint(f"{col['pink']}Obtaining{col['reset']}: FDT Matrix")
    matrix = load_fdt_matrix(os.path.join(args["fdt_path"], "fdt_matrix2.dot"))
    dr_regression = nmf_dual_regression if args["algo"] else ica_dual_regression
    nprint(f"{col['pink']}Running{col['reset']}: Dual Regression", to_flush=True)
    dr_results = run_decomp(dr_regression, components, matrix, args["parallel"])
    nprint(f"{col['pink']}Saving{col['reset']}: Components", flush=True)
    save_dual_regression_images(
        dr_results,
        args["output_dir"],
        args["seeds"],
        args["algo"].upper(),
        dr_results["white_components"].shape[0],
        args["id"],
        args["fdt_path"],
        args["roi"],
    )
    nprint(f"{col['pink']}Completed{col['reset']}: {args['id']}", to_flush=True)
    return None


if __name__ == "__main__":
    args = cluster_mode_args()
    dual_regression_pipeline(args)
