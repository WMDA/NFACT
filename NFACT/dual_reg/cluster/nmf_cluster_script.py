import argparse


def nmf_script_args():
    parser = argparse.ArgumentParser(description="Run NMF dual regression.")
    parser.add_argument(
        "--output_dir", required=True, help="Directory to save the output components."
    )
    return vars(parser.parse_args())
