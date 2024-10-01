"""
This is a custom linting script to
check that variable names are longer than
bigger than one
"""

import ast
import os
import argparse
from NFACT.NFACT_base.utils import colours


class VariableNameChecker(ast.NodeVisitor):
    def __init__(self):
        self.bad_variable_names = []

    def visit_Name(self, node):
        # Check if the variable name is a single character
        if isinstance(node.ctx, ast.Store) and len(node.id) == 1:
            self.bad_variable_names.append((node.id, node.lineno))
        self.generic_visit(node)


def check_script_for_bad_variable_names(script_path):
    with open(script_path, "r") as file:
        tree = ast.parse(file.read(), filename=script_path)

    checker = VariableNameChecker()
    checker.visit(tree)

    if checker.bad_variable_names:
        col = colours()
        accepted_shorted_variables = ["_"]
        for var_name, lineno in checker.bad_variable_names:
            if var_name in accepted_shorted_variables:
                continue
            print(
                f"{col['red']}Bad variable names found in {script_path}:{col['reset']}"
            )
            print(
                f"{col['pink']}\t-> Line {lineno}: '{var_name}' is too short{col['reset']}"
            )


def check_directory_for_bad_variable_names(directory_path, ignore_dirs):
    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [
            directory
            for directory in dirs
            if os.path.join(root, directory) not in ignore_dirs
        ]

        for file in files:
            if file.endswith(".py"):
                script_path = os.path.join(root, file)
                check_script_for_bad_variable_names(script_path)


def args():
    option = argparse.ArgumentParser()
    option.add_argument(
        "-d", "--directory", dest="directory", help="directory to run linting on"
    )
    return vars(option.parse_args())


if __name__ == "__main__":
    arg = args()
    directories_to_ignore = ["dev", "NFACT_GLM"]
    check_directory_for_bad_variable_names(
        arg["directory"],
        [
            os.path.join(arg["directory"], directory)
            for directory in directories_to_ignore
        ],
    )
