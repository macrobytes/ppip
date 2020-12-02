from typing import Dict, List, Any
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor


class ParallelInstaller:
    def __init__(
        self,
        requirements_json: Dict[str, Any],
        threads: int,
        pip_path: str,
        target: str,
        skip_dependency_check: bool,
        no_cache_dir: bool,
    ):
        """
        Instantiates the ParallelInstaller object, used for install python
        packages in parallel
        :param requirements_json: Dict[str, Any]
            The output of `pipdeptree --json-tree`
        :param threads: int
            The number of workers in the ThreadPoolExecutor
        :param pip_path: str
            Location of pip/pip3 on the filesystem (default: /usr/bin/pip3)
        :param target: str
            Target directory to install packages; if None the default path
            will be used.
        :param skip_dependency_check: bool
            If true, pip will install with the --no-deps flag
        :param no_cache_dir: bool
            If true, pip will install with the --no-cache-dir flag.
        """
        self._requirements_json = requirements_json
        self._threads = threads
        self._pip_path = pip_path
        self._target = target
        self._skip_dependency_check = skip_dependency_check
        self._dependency_tree = []
        self._no_cache_dir = no_cache_dir

    def _install_package(self, pkg: str):
        installation_cmd = [self._pip_path, "install", pkg]
        if self._no_cache_dir:
            installation_cmd.append("--no-cache-dir")
        if self._skip_dependency_check:
            installation_cmd.append("--no-deps")
        if self._target:
            installation_cmd.append("--target")
            installation_cmd.append(self._target)

        try:
            subprocess.check_output(installation_cmd)
        except subprocess.CalledProcessError as e:
            print(e.returncode)
            sys.exit(e.returncode)

    def _remove_leaf_nodes(
        self, dependency_tree: Dict[str, Any], leaf_nodes=None
    ) -> List[str]:
        if leaf_nodes is None:
            leaf_nodes = []

        idx = 0
        while True:
            if idx == len(dependency_tree):
                break
            elif len(dependency_tree[idx]["dependencies"]) == 0:
                pkg = (
                    dependency_tree[idx]["key"]
                    + "=="
                    + dependency_tree[idx]["installed_version"]
                )
                leaf_nodes.append(pkg)
                del dependency_tree[idx]
            else:
                self._remove_leaf_nodes(
                    dependency_tree[idx]["dependencies"], leaf_nodes
                )
                idx += 1
        return set(leaf_nodes)

    def _flatten_dependency_tree(self):
        tree = list(self._requirements_json)
        dependency_set = set()
        while len(tree) > 0:
            dependency_set = dependency_set.union(self._remove_leaf_nodes(tree))
        self._dependency_tree = list([dependency_set])

    def _build_dependency_tree(self):
        tree = list(self._requirements_json)
        while len(tree) > 0:
            self._dependency_tree.append(self._remove_leaf_nodes(tree))

        current_level = len(self._dependency_tree) - 1
        for level in range(current_level - 1, -1, -1):
            for dependency in set(self._dependency_tree[level]):
                try:
                    self._dependency_tree[current_level].remove(dependency)
                except:
                    ...
            current_level -= 1
            if current_level == 0:
                break

    def install(self):
        """
        Installs the python packages specified in the requirements JSON
        """
        if self._skip_dependency_check:
            self._flatten_dependency_tree()
        else:
            self._build_dependency_tree()
        with ThreadPoolExecutor(max_workers=self._threads) as executor:
            for level in self._dependency_tree:
                for dependency in level:
                    executor.submit(self._install_package, (dependency))
