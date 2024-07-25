from NFACT.NFACT_PP.nfactpp import surf_volume_main, hcp_stream_main
from NFACT.NFACT_PP.nfactpp_args import nfact_pp_args

from NFACT.NFACT_PP.nfactpp_setup import (
    check_fsl_is_installed,
    check_study_folder,
    list_of_subjects_from_directory,
    check_arguments,
    check_ptx_options_are_valid,
)

from NFACT.utils.utils import error_and_exit, Signit_handler, read_file_to_list
from NFACT.setup.configure_setup import (
    return_list_of_subjects_from_file,
    does_list_of_subjects_exist,
    check_subject_exist,
)


def nfact_pp_main():
    """
    Main nfact_pp function.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    arg = nfact_pp_args()
    handler = Signit_handler()

    # Check that complusory arguments given
    check_arguments(arg)

    # Error handle if FSL not installed or loaded
    error_and_exit(
        check_fsl_is_installed(),
        "FSLDIR not in path. Check FSL is installed or has been loaded correctly",
    )

    # Error handle if study directory not given
    error_and_exit(check_study_folder(arg["study_folder"]))

    # Error handle list of subjects
    if arg["list_of_subjects"]:
        error_and_exit(
            does_list_of_subjects_exist(arg["list_of_subjects"]),
            "List of subjects doesn't exist.",
        )

        arg["list_of_subjects"] = return_list_of_subjects_from_file(
            arg["list_of_subjects"]
        )

        # Error handles if not subjects can be found.
        error_and_exit(
            arg["list_of_subjects"],
            "Unable to locate subjects. Please check data structure",
        )

    if not arg["list_of_subjects"]:
        arg["list_of_subjects"] = list_of_subjects_from_directory(arg["study_folder"])

        error_and_exit(
            arg["list_of_subjects"], "Unable to find list of subjects from directory"
        )
    check_subject_exist(arg["list_of_subjects"])
    if arg["ptx_options"]:
        try:
            arg["ptx_options"] = read_file_to_list(arg["ptx_options"])
            arg["ptx_options"] = [arg.strip() for arg in arg["ptx_options"]]

        except Exception as e:
            error_and_exit(False, f"Unable to read ptx_options text file due to {e}")
        check_ptx_options_are_valid(arg["ptx_options"])

    if arg["hcp_stream"]:
        hcp_stream_main(arg, handler)

    surf_volume_main(arg, handler)


if __name__ == "__main__":
    nfact_pp_main()
