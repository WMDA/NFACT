from NFACT.dual_reg.nfact_dr_functions import get_group_level_components
from NFACT.base.setup import check_medial_wall
from NFACT.base.matrix_handling import load_fdt_matrix
from NFACT.dual_reg.dual_regression import nmf_dual_regression, ica_dual_regression
from NFACT.dual_reg.nfact_dr_functions import save_dual_regression_images
import argparse


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
    parser.add_argument("--algo", required=True, help="Which algo to run")
    parser.add_argument("--seeds", required=True, help="Path to seeds.")
    parser.add_argument("--id", required=True, help="Subject ID.")
    parser.add_argument("--medial_wall", default=False, help="Path to medial wall.")
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

    if args["medial_wall"]:
        args["surface"] = True
        args = check_medial_wall(args)
    else:
        args["surface"] = False

    print("Obtaining Group Level Components")
    components = get_group_level_components(
        args["component_path"],
        args["group_average_path"],
        args["seeds"],
        args["medial_wall"],
    )

    print("Obtaining FDT Matrix")
    matrix = load_fdt_matrix(args["fdt_path"])
    dr_regression = nmf_dual_regression if args["algo"] else ica_dual_regression
    print("Running Dual Regression")
    dr_results = dr_regression(components, matrix)

    print("Saving Components")
    save_dual_regression_images(
        dr_results,
        args["output_dir"],
        args["seeds"],
        args["algo"].upper(),
        dr_results["white_components"].shape[0],
        args["id"],
        args["medial_wall"],
    )
    return None


if __name__ == "__main__":
    args = script_args()
    main_dr(args)
