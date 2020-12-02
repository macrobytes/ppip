import argparse
from installer.parallel_installer import ParallelInstaller
from typing import Dict, Any
import json
import sys


def build_dependency_json(requirements_json_path: str) -> Dict[str, Any]:
    """
    Returns a dictionary representation of the JSON object stored in the
    requirements file.
    """
    try:
        with open(requirements_json_path, "r") as fh:
            try:
                requirements_json = json.loads(fh.read())
                return requirements_json
            except:
                print(f"{requirements_json_path} does not appear to be valid JSON.")
                sys.exit(1)
    except:
        print(f"Unable to read from {requirements_json_path}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--threads",
        default=1,
        type=int,
        help="number of threads used to install packages",
    )

    parser.add_argument(
        "--requirements-path",
        required=True,
        type=str,
        help="/path/to/requirements.json (the output of `pipdeptree --json-tree`)",
    )

    parser.add_argument(
        "--pip-path",
        default="/usr/bin/pip3",
        type=str,
        help="/path/to/python-pip (e.g. /usr/bin/pip3)",
    )

    parser.add_argument(
        "--target",
        type=str,
        help="target path to install python packages (e.g. /path/to/target)",
    )

    parser.add_argument(
        "--skip-dependency-check",
        action="store_true",
        help=(
            "If specified, pip will install with the --no-deps flag;"
            " recommended if the requirements.json is exhaustive."
        ),
    )

    parser.add_argument(
        "--no-cache-dir",
        action="store_true",
        help="If specified, pip will install with the --no-cache-dir flag."
    )

    args = parser.parse_args()
    requirements_json = build_dependency_json(args.requirements_path)
    installer = ParallelInstaller(
        requirements_json=requirements_json,
        threads=args.threads,
        pip_path=args.pip_path,
        target=args.target,
        skip_dependency_check=args.skip_dependency_check,
        no_cache_dir=args.no_cache_dir,
    )
    installer.install()


if __name__ == "__main__":
    main()
