import unittest
import json
from parallel_installer import ParallelInstaller


class ParallelInstallerTest(unittest.TestCase):
    def _build_installer(self):
        return ParallelInstaller(
            requirements_json=self._get_requirements_json(),
            threads=1,
            pip_path="/usr/bin/pip3",
            target="/tmp/ppip-target-path-2",
            skip_dependency_check=True,
            no_cache_dir=False,
        )

    def _get_requirements_json(self):
        with open("test_data/requirements.json") as fh:
            return json.loads(fh.read())

    def test_remove_leaf_nodes(self):
        installer = self._build_installer()
        
        dependency_tree = list(installer._requirements_json)
        leaf_nodes = installer._remove_leaf_nodes(dependency_tree)
        assert 6 == len(set(leaf_nodes))
        assert 'numpy==1.19.4' in leaf_nodes
        assert 'scipy==1.5.4' not in leaf_nodes

    def test_flatten_dependency_tree(self):
        installer = self._build_installer()
        installer._flatten_dependency_tree()
        assert 10 == len(installer._dependency_tree[0])
        assert "pandas==1.1.4" in installer._dependency_tree[0]

    def test_build_dependency_tree(self):
        installer = self._build_installer()
        installer._build_dependency_tree()
        assert 3 == len(installer._dependency_tree)
        assert "pandas==1.1.4" in installer._dependency_tree[2]

if __name__ == "__main__":
    unittest.main()
