import os
import numpy as np
import nibabel as nib
from sklearn.preprocessing import StandardScaler
from glob import glob
from NFACT.base.utils import colours


def save_nifti(data: np.array, affine: np.array, filename: str) -> None:
    """
    Function to save nifti file from a
    numpy array

    Parameters
    ---------
    data: np.array
        array of data to save as image
    affine: np.array
        affine of image
    filename: str
        filename of image to save

    Returns
    -------
    None
    """
    new_img = nib.Nifti1Image(data.astype(np.float32), affine)
    nib.save(new_img, filename)


def normalization(img_data: np.array) -> np.array:
    """
    Function to normalise an image

    Parameters
    ----------
    img_data: np.array
        array of data to normalise

    Returns
    -------
    zscores: np.array
        array of zscores reshaped
        to be saved as a imge
    """
    n_voxels = np.prod(img_data.shape[:-1])
    n_vol = img_data.shape[-1]
    reshaped_data = img_data.reshape(n_voxels, n_vol)
    non_zero_mask = ~(reshaped_data == 0).all(axis=1)
    z_scores = np.zeros_like(reshaped_data)
    scaler = StandardScaler()
    z_scores[non_zero_mask] = scaler.fit_transform(reshaped_data[non_zero_mask])
    return z_scores.reshape(img_data.shape)


def hitcount(comp_scores: np.array, threshold: int) -> dict:
    """
    Function to count up the number of times

    Parameters
    ----------
    comp_scores: np.array
       component scores
    threshold: int
        threshold components at

    Return
    ------
    dict: dictionary
        dict of hitcount
        and bin_mask
    """
    binary_masks = np.abs(comp_scores) > threshold
    return {"hitcount": np.sum(binary_masks, axis=-1), "bin_mask": binary_masks}


def binary_mask(binary_masks: np.array) -> np.ndarray:
    """
    Function to create binary mask from
    numpy array

    Parameteres
    -----------
    binary_masks: np.array
         array of

    Returns
    --------
    np.ndarray: np.array
        numpy array of
    """
    return np.any(binary_masks, axis=-1).astype(np.uint8)


def scoring(img_data: np.array, normalize: bool, threshold: int) -> dict:
    if normalize:
        return {"scores": normalization(img_data), "threshold": threshold}
    return {"scores": img_data, "threshold": 0}


def hitcount_maps(img_data: np.array, threshold: int, normalize=True) -> dict:
    """
    Function to create a binary coverage mask
    and a hitmap of voxels

    Parameters
    ----------
    img_data: np.array
        Array of image data
    threshold: int
        value to threshold array at

    Returns
    --------
    dictionary: dict
        dictionary of hitcount and bin mask
    """

    comp_scores = scoring(img_data, normalize, threshold)
    return hitcount(comp_scores["scores"], comp_scores["threshold"])


def coverage_maps(img_path: str, img_name: str, threshold: int, normalize=True) -> None:
    """
    Wrapper function to create a binary coverage mask
    and a hitmap of voxels. Saves images

    Parameters
    ----------
    img_path: str
        path to image
    img_name: str
        name of image
    threshold: int
        value to thres

    Returns
    --------
    float: float
       float of percentage coverage
    """
    col = colours()
    img_comp = nib.load(img_path)
    img_data = img_comp.get_fdata()
    maps = hitcount_maps(img_data, threshold, normalize)
    print(f"{col['pink']}Image:{col['reset']} Saving Hitmap")
    save_nifti(maps["hitcount"], img_comp.affine, img_name)
    coverage_map_mask = binary_mask(maps["bin_mask"])
    image_name_mask = os.path.join(
        os.path.dirname(img_name), f"mask_{os.path.basename(img_name)}"
    )
    print(f"{col['pink']}Image:{col['reset']} Saving Binary Mask")
    save_nifti(coverage_map_mask, img_comp.affine, image_name_mask)


def get_images(nfact_directory: str, dim: str, algo: str) -> dict:
    """
    Function to get images

    Parameters
    -----------
    nfact_directory: str
        path to nfact directory
    dim: str
        str of dimensions
    algo: str
        either NMF or ICA

    Returns
    -------
    dict: dictionary
         dict of grey and white images
    """
    return {
        "grey_images": glob(
            os.path.join(
                nfact_directory, "components", algo, "decomp" f"G_{algo}_dim{dim}*"
            )
        ),
        "white_image": os.path.join(
            nfact_directory, "components", algo, "decomp" f"W_{algo}_dim{dim}.nii.gz"
        ),
    }
