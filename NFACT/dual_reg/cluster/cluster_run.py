from ..dual_regression import get_subject_id


def run_on_cluster(args: dict, paths: dict) -> None:
    sub_id = get_subject_id(
        paths[""],
    )

    return None
