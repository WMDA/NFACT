from NFACT.dual_reg.nfact_dr_functions import get_group_level_components
from NFACT.base.matrix_handling import load_fdt_matrix
from NFACT.dual_reg.dual_regression import nmf_dual_regression
from NFACT.dual_reg.nfact_dr_functions import save_dual_regression_images
import argparse


def nmf_script_args() -> dict:
    """
    NMF args

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary
        dict of cmd options
    """
    parser = argparse.ArgumentParser(description="Run NMF dual regression")
    parser.add_argument(
        "--output_dir", required=True, help="Directory to save the output components."
    )
    parser.add_argument(
        "--component_path", required=True, help="Directory to components path."
    )
    parser.add_argument(
        "--group_average_path", required=True, help="Path to group averages."
    )
    parser.add_argument("--seeds", required=True, help="Path to seeds.")
    parser.add_argument("--id", required=True, help="Subject ID.")
    parser.add_argument("--medial_wall", default=False, help="Path to medial wall.")
    return vars(parser.parse_args())


def main(args: dict) -> None:
    components = get_group_level_components(
        args["component_path"],
        args["group_average_path"],
        args["seeds"],
        args["medial_wall"],
    )
    matrix = load_fdt_matrix(args["fdt_path"])
    dr_results = nmf_dual_regression(components, matrix)
    save_dual_regression_images(
        dr_results,
        args["output_dir"],
        args["seeds"],
        "NMF",
        dr_results["white_components"].shape[0],
        args["id"],
        args["medial_wall"],
    )
    return None


if __name__ == "__main__":
    args = nmf_script_args()
    main(args)
