from ..nfact_dr_functions import get_subject_id
from NFACT.base.utils import nprint, colours
from NFACT.base.cluster_support import cluster_submission


def bind_string(fdt_directory: str, decomp_dir: str, output_dir: str) -> str:
    """
    Function to return the binding
    for

    Parameters
    ----------
    bind_path: str
        string of bindings

    Returns
    -------

    """
    return f"""
--bind {fdt_directory}:{fdt_directory},{decomp_dir}:{decomp_dir},{output_dir}:{output_dir}
"""


def singulairty_command(
    bind_string: str,
    sif_path: str,
    output_dir: str,
    component_path: str,
    group_average_path: str,
    algo: str,
    sub_id: str,
    medial_wall: str,
    fdt_path: str,
) -> str:
    """
    Function to return singularity
    command.

    Parameters
    ---------
    bind_path: str
        bind path for singularity container
    sif_path: str
        path to singulairty image
    output_dir: str
        path to output directory
    component_path: str

    group_average_path: str,
    algo: str,
    sub_id: str,
    medial_wall: str
    """

    command = f"""
singularity run --oci {bind_string} {sif_path} \\
    --output_dir {output_dir} \\
    --component_path {component_path} \\
    --group_average_path {group_average_path} \\
    --algo {algo} \\
    --fdt_path {fdt_path} \\
    --id {sub_id} 
"""
    if medial_wall:
        command += f""" \\ 
        --medial_wall {medial_wall}"""
    return command


def build_cluster_command():
    bind_path = bind_string()
    return None


def submit_to_cluster(fdt_matricies):
    job_ids = []
    for sub, idx in enumerate(fdt_matricies):
        sub_id = get_subject_id(sub, idx)
        cluster_command = build_cluster_command()
        id = cluster_submission(cluster_command)
        job_ids.append(id)
    return job_ids


def run_on_cluster(args: dict, paths: dict) -> None:
    col = colours()
    nprint(f"{col['pink']}Running{col['reset']}: Cluster")
    nprint("")
    return None
