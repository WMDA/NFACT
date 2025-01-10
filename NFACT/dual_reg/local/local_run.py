from ..dual_regression import ica_dual_regression, nmf_dual_regression
from ..nfact_dr_functions import get_group_level_components
from ..nfact_dr_functions import save_dual_regression_images
from NFACT.base.utils import nprint, colours
from NFACT.base.matrix_handling import normalise_components
from NFACT.base.matrix_handling import load_fdt_matrix
from NFACT.base.utils import error_and_exit

import numpy as np
import re
import os


def run_locally(args: dict, paths: dict):
    """
    nfact_dr local run function

    Parameters
    ----------
    args: dict
        dictionary of cmd args
    paths: dict
        path to images

    Returns
    -------
    None
    """
    col = colours()

    nprint(f"{col['pink']}Running:{col['reset']} Locally")
    nprint(f"{col['pink']}Obtaining:{col['reset']} Components")
    nprint("-" * 100)
    components = get_group_level_components(
        paths["component_path"],
        paths["group_average_path"],
        args["seeds"],
        args["medial_wall"],
    )

    method = "Regression" if args["algo"] == "ica" else "Non-negative Regression"
    nprint(f"{col['pink']}DR Method:{col['reset']} {method}")

    dual_reg = Dual_regression(
        algo=args["algo"],
        normalise=args["normalise"],
        parallel=False,
        list_of_files=args["ptxdir"],
        component=components,
        seeds=args["seeds"],
        nfact_directory=os.path.join(args["outdir"], "nfact_dr"),
        medial_wall=args["medial_wall"],
    )
    dual_reg.run()


class Dual_regression:
    """
    Dual regression Class.
    Will perform Dual regression
    to get subject specific maps
    from group components.

    Performs nnon negative least
    squares regression for NFM components to
    maintain negative values.

    Usage
    -----
    dual_reg = Dual_regression(
            algo="ICA"
            normalise=False,
            parallell=False,
            list_of_files=list_of_subjects,
            component=components,
            seeds=seeds,
            nfact_directory=/path/to/nfact_dir)
    dual_reg.run()
    """

    def __init__(
        self,
        algo: str,
        normalise: bool,
        parallel: bool,
        list_of_files: list,
        component: dict,
        seeds: list,
        nfact_directory: str,
        medial_wall: list,
    ) -> None:
        self.algo = algo
        self.normalise = normalise
        self.parallel = parallel
        self.list_of_file = list_of_files
        self.component = component
        self.seeds = seeds
        self.nfact_directory = nfact_directory
        self.medial_wall = medial_wall

    def run(self) -> None:
        """
        Main method to run dual regression.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.parallel:
            print("Not implemented yet. Running single subject regression")
            self.__run_dual_regress_single()
        if not self.parallel:
            self.__run_dual_regress_single()

    def __run_dual_regress_single(self) -> None:
        """
        Runs non parallel regression.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        decomp = self.__decomp_method()
        col = colours()
        for idx, subject in enumerate(self.list_of_file):
            subject_id = self.__get_subject_id(subject, idx)
            nprint(
                f"\n{col['pink']}Dual regressing on subject:{col['reset']} {subject_id}"
            )
            connectivity_matrix = self.__connecitivity_matrix(subject)

            try:
                components = decomp(connectivity_matrix)
            except ValueError as e:
                error_and_exit(
                    False,
                    f"Components have incompatable size with connectivity Matrix {e}",
                )
            except Exception as e:
                error_and_exit(False, f"Unable to perform dual regression due to {e}")
            if self.normalise:
                normalised = normalise_components(
                    components["grey_components"], components["white_components"]
                )
                components["normalised_white"] = normalised["white_matter"]
                components["normalised_grey"] = normalised["grey_matter"]
            self.__save_image(components, subject, subject_id)

    def __decomp_method(self) -> object:
        """
        Method to decide on method type.

        Parameters
        ----------
        None

        Returns
        --------
        object: regression function
           either self.__ica_dual_regression
           or self.__nmf_dual_regression
        """
        return ica_dual_regression if self.algo == "ica" else nmf_dual_regression

    def __connecitivity_matrix(self, subject: str) -> np.ndarray:
        """
        Method to load_fdt_matrix.

        Parameteres
        -----------
        subject: str
            path to subjects fdt_matrix2

        Returns
        -------
        np.ndarray: array
            loaded fdt matrix
        """
        return load_fdt_matrix(os.path.join(subject, "fdt_matrix2.dot"))

    def __save_image(self, components: dict, subject: str, subject_id) -> None:
        """
        Method to save regression images

        Parameteres
        -----------
        components: dict
            dictionary of components
        subject: str
            path to subjects fdt_matrix2
        subject_id: str
            string of subjects id

        Returns
        -------
        None

        """
        save_dual_regression_images(
            components,
            self.nfact_directory,
            self.seeds,
            self.algo.upper(),
            self.component["white_components"].shape[0],
            subject_id,
            subject,
            self.medial_wall,
        )

    def __get_subject_id(self, path: str, number: int) -> str:
        """
        Method to assign a subjects Id

        Parameters
        ----------
        path: str
            string of path to subjects
        number: int
            subject number

        Returns
        ------
        str: string
            subject id either taken from file path
            or assigned number in the list
        """
        try:
            return re.findall(r"sub[a-zA-Z0-9]*", path)[0]
        except IndexError:
            sub_name = os.path.basename(os.path.dirname(path))
            if "MR" in sub_name:
                try:
                    return sub_name.split("_")[0]
                except IndexError:
                    pass
            return f"sub-{number}"
