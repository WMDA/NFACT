from sklearn.preprocessing import StandardScaler
import numpy as np


def dualreg(Cs, X, normalise=False):
    """Dual regression of C on X where C is a group mat and X is either G or W
    We have :  C = G*W
    So either:
        Cs = G*Ws
    or:
        Cs' = W'*Gs'
    Input:
    Cs: 2d array - individual subject connectivity matrix
    Outputs:
    Gs : 2d array
    Ws : 2d array
    """
    # if X is G, then X.shape[0] is same as Cs.shape[0]
    if X.shape[0] == Cs.shape[0]:
        # X is G
        Ws = np.linalg.pinv(X) @ Cs
        Gs = (np.linalg.pinv(Ws.T) @ Cs.T).T
    # if X is W, then X.shape[1] is same as Cs.shape[1] (remember W is in fact W.T)
    elif X.shape[1] == Cs.shape[1]:
        # X is W
        Gs = (np.linalg.pinv(X.T) @ Cs.T).T
        Ws = np.linalg.pinv(Gs) @ Cs

    if normalise:
        Gs = StandardScaler().fit_transform(Gs)
        Ws = StandardScaler().fit_transform(Ws.T).T

    return Gs, Ws


# def
def ICA_dual_regression(
    connectivity_matrix: np.array,
    component: np.array,
) -> np.darray:
    """
    Dual regression function for ICA.
    Regresses the invidiual connectivity matrix
    onto the group components.

    If white matter component then regresses
    grey matter map onto connectivity matrix and vice versa.


    """
    wm_component_grey_weights = (
        np.linalg.pinv(component["white_components"].T) @ connectivity_matrix.T
    ).T
    wm_component_white_weights = (
        np.linalg.pinv(wm_component_grey_weights) @ connectivity_matrix
    )
    gm_component_white_weights = (
        np.linalg.pinv(component["grey_components"]) @ connectivity_matrix
    )
    gm_component_grey_weights = (
        np.linalg.pinv(gm_component_white_weights.T) @ connectivity_matrix.T
    ).T

    return {
        "white_matter": wm_component_white_weights,
        "grey_matter": gm_component_grey_weights,
    }
