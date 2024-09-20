from NFACT.NFACT_decomp.decomposition.matrix_handling import avg_fdt
from NFACT.NFACT_decomp.decomposition.decomp import (
    melodic_incremental_group_pca,
    ica_decomp,
    get_parameters,
    nmf_decomp,
    sign_flip,
)
from NFACT.NFACT_decomp.pipes.image_handling import create_wta_map
from NFACT.NFACT_base.matrix_handling import normalise_components
import pytest
from pathlib import Path


@pytest.fixture
def test_matrix():
    current_working_dir = Path(__file__).parent
    list_of_mat = [
        f"{current_working_dir}/test_data/sub-0_fdt_matrix2.dot",
        f"{current_working_dir}/test_data/sub-1_fdt_matrix2.dot",
        f"{current_working_dir}/test_data/sub-2_fdt_matrix2.dot",
    ]
    return avg_fdt(list_of_mat)


def test_load_worked(test_matrix):
    assert test_matrix is not None


@pytest.fixture
def test_pca(test_matrix):
    return melodic_incremental_group_pca(test_matrix, 10, 10)


def test_pca_worked(test_pca):
    assert test_pca is not None


@pytest.fixture
def test_ICA_hyperparameters():
    return get_parameters(None, "ica", 10)


@pytest.fixture
def test_NMF_hyperparameters():
    return get_parameters(None, "nmf", 10)


def test_hyperparameters_ICA_worked(test_ICA_hyperparameters):
    assert test_ICA_hyperparameters is not None


def test_hyperparameters_NMF_worked(test_NMF_hyperparameters):
    assert test_NMF_hyperparameters is not None


@pytest.fixture
def test_ica(test_pca, test_ICA_hyperparameters, test_matrix):
    return ica_decomp(test_ICA_hyperparameters, test_pca, test_matrix)


def test_ica_worked(test_ica):
    assert test_ica is not None


@pytest.fixture
def test_nmf(test_NMF_hyperparameters, test_matrix):
    return nmf_decomp(test_NMF_hyperparameters, test_matrix)


def test_nmf_worked(test_nmf):
    assert test_nmf is not None


def test_normalise_comp(test_ica):
    norm_comp = normalise_components(
        test_ica["grey_components"], test_ica["white_components"], True
    )
    assert norm_comp is not None


def test_signflip(test_ica):
    assert sign_flip(test_ica["white_components"]) is not None


def test_wta(test_ica):
    assert create_wta_map(test_ica["white_components"], 0, 0.0, True) is not None
