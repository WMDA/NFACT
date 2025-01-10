def bind_string(bind_path) -> str:
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
--bind {bind_path}:{bind_path}
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
singularity exec {bind_string} {sif_path} \\
    --output_dir {output_dir} \\
    --component_path {component_path} \\
    --group_average_path {group_average_path} \\
    --algo {algo} \\
    --id {sub_id} 
"""
    if medial_wall:
        command += f""" \\ 
        --medial_wall {medial_wall}"""
    return command
