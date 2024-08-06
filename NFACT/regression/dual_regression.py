from NFACT.decomposition.decomp import normalise_components
from NFACT.decomposition.matrix_handling import load_fdt_matrix
import numpy as np
from scipy.optimize import nnls


def dualreg(
    connectivity_matrix: np.array,
    components: dict,
    algo: str,
    normalise: str,
    glm: bool = False,
):
    """
    Wrapper function to perform dual regression
    and save results

    Parameters
    ----------
    connectivity_matrix: np.array
        connectivity matrix of a single subject
    component: dict
        dictionary of components
    """

    if algo == "ica":
        dual_reg = ICA_dual_regression(connectivity_matrix, components)
    if algo == "nfm":
        return
    if normalise:
        demean = True if algo == "ica" else False
        normalise_components(dual_reg["grey_matter"], dual_reg["white_matter"], demean)

    if glm:
        return dual_reg


class Dual_regression:
    
    def __init__(self, 
                 algo, 
                 normalise, 
                 parallel,
                 list_of_files,
                 component) -> None:
        
        self.algo = algo
        self.normalise = normalise
        self.parallel = parallel
        self.list_of_file = list_of_files 
        self.component = component
    
    def fit(self):
        if self.parallel:
            return None
        if not self.parallel:
            return None
    def run_dual_regress_single(self):
        for subject in self.list_of_file:
            return None


    def ICA_dual_regression(self,

        ) -> dict:
            """
            Dual regression method for ICA.
            Regresses the invidiual connectivity matrix
            onto the group components.
        
            If white matter component then regresses
            grey matter map onto connectivity matrix and vice versa.
        
            """
            self.wm_component_grey_map = (
                np.linalg.pinv(self.component["white_components"].T) @ self.connectivity_matrix.T
            ).T
            self.wm_component_white_map = np.linalg.pinv(self.wm_component_grey_map) @ self.connectivity_matrix
            self.gm_component_white_map = (
                np.linalg.pinv(self.component["grey_components"]) @ self.connectivity_matrix
            )
            self.gm_component_grey_map = (
                np.linalg.pinv(self.gm_component_white_map.T) @ self.connectivity_matrix.T
            ).T
        

    def nfm_dual_regression(self, connectivity_matrix, component, dim):
        return np.array([nnls(component, connectivity_matrix[:, col])[0] for col in range(connectivity_matrix.shape[dim])]).T
    
    def return_data_for_glm(self)
        return {
                "white_matter": self.wm_component_white_map,
                "grey_matter": self.gm_component_grey_map,
            }
    

#TODO: shape needs checking depending on what component is being 
def nfm_dual_regression(connectivity_matrix, component):
    return np.array([nnls(component, connectivity_matrix[:, i])[0] for i in range(connectivity_matrix.shape[1])]).T


# def
def ICA_dual_regression(
    connectivity_matrix: np.array,
    component: dict,
) -> dict:
    """
    Dual regression function for ICA.
    Regresses the invidiual connectivity matrix
    onto the group components.

    If white matter component then regresses
    grey matter map onto connectivity matrix and vice versa.

    Parameters
    ----------
    connectivity_matrix: np.array
        connectivity matrix of a single subject
    component: dict
        dictionary of components

    Returns
    -------
    dictionary: dict
        dictionary of grey and white matter components


    """
    wm_component_grey_map = (
        np.linalg.pinv(component["white_components"].T) @ connectivity_matrix.T
    ).T
    wm_component_white_map = np.linalg.pinv(wm_component_grey_map) @ connectivity_matrix
    gm_component_white_map = (
        np.linalg.pinv(component["grey_components"]) @ connectivity_matrix
    )
    gm_component_grey_map = (
        np.linalg.pinv(gm_component_white_map.T) @ connectivity_matrix.T
    ).T

    return {
        "white_matter": wm_component_white_map,
        "grey_matter": gm_component_grey_map,
    }
