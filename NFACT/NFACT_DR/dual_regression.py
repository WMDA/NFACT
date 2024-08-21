from .nfact_dr_functions import save_dual_regression_images
from NFACT.NFACT_decomp.decomposition.decomp import normalise_components
from NFACT.NFACT_decomp.decomposition.matrix_handling import load_fdt_matrix
from NFACT.NFACT_base.utils import error_and_exit

import numpy as np
from scipy.optimize import nnls
import re
import os


# TODO: Add in parallelization.
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
            save
        )
    dual_reg.run()
    """

    def __init__(
        self,
        algo: str,
        normalise: bool,
        parallel: bool,
        list_of_files: list,
        component: dict,
        save_type: str,
        seeds: list,
        nfact_directory: str,
    ) -> None:
        self.algo = algo
        self.normalise = normalise
        self.parallel = parallel
        self.list_of_file = list_of_files
        self.component = component
        self.save_type = save_type
        self.seeds = seeds
        self.nfact_directory = nfact_directory

    def run(self) -> None:
        """
        Main method to run dual regression
        """
        if self.parallel:
            print("Not implemented yet")
            return None
        if not self.parallel:
            self.__run_dual_regress_single()

    def __run_dual_regress_single(self) -> None:
        """
        Runs non parallel regression
        """
        decomp = (
            self.__ICA_dual_regression
            if self.algo == "ica"
            else self.__nfm_dual_regression
        )

        for idx, subject in enumerate(self.list_of_file):
            self.__get_subject_id(subject, idx)
            print(f"Dual regressing on {self.subject_id}:")
            self.connectivity_matrix = load_fdt_matrix(
                os.path.join(subject, "fdt_matrix2.dot")
            )
            try:
                components = decomp()
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
            save_dual_regression_images(
                self.save_type,
                components,
                self.nfact_directory,
                self.seeds,
                self.algo.upper(),
                self.component["white_components"].shape[0],
                self.subject_id,
                subject,
            )

    def __get_subject_id(self, path, number):
        """
        Method to assign a subjects Id
        """
        try:
            self.subject_id = re.findall(r"sub[a-zA-Z0-9]*", path)[0]
        except Exception:
            self.subject_id = f"sub-{number}"

    def __ICA_dual_regression(
        self,
    ) -> dict:
        """
        Dual regression method for ICA.
        Regresses the invidiual connectivity matrix
        onto the group components.

        If white matter component then regresses
        grey matter map onto connectivity matrix and vice versa.

        Parameters
        ----------
        None

        Returns
        -------
        dict: dictionary
            dictionary of components
        """

        wm_component_grey_map = (
            np.linalg.pinv(self.component["white_components"].T)
            @ self.connectivity_matrix.T
        ).T
        wm_component_white_map = (
            np.linalg.pinv(wm_component_grey_map) @ self.connectivity_matrix
        )

        gm_component_grey = (
            np.linalg.pinv(self.component["grey_components"]) @ self.connectivity_matrix
        )
        gm_component_grey_map = (
            np.linalg.pinv(gm_component_grey.T) @ self.connectivity_matrix.T
        ).T

        return {
            "grey_components": gm_component_grey_map,
            "white_components": wm_component_white_map,
        }

    def __nfm_dual_regression(self) -> None:
        """
        Dual regression method for NFM.
        """
        wm_component_white_map = np.array(
            [
                nnls(
                    self.component["grey_components"], self.connectivity_matrix[:, col]
                )[0]
                for col in range(self.connectivity_matrix.shape[1])
            ]
        ).T
        gm_component_grey_map = np.array(
            [
                nnls(wm_component_white_map.T, self.connectivity_matrix.T[:, col])[0]
                for col in range(self.connectivity_matrix.shape[0])
            ]
        )

        return {
            "grey_components": gm_component_grey_map,
            "white_components": wm_component_white_map,
        }
