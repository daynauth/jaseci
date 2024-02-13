"""The Jac Programming Language."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

from jaclang.plugin.default import JacBuiltin, JacFeatureDefaults  # noqa: E402
from jaclang.plugin.feature import JacFeature, pm  # noqa: E402
from jaclang.vendor import lark  # noqa: E402
from jaclang.vendor import mypy  # noqa: E402
from jaclang.vendor import pluggy  # noqa: E402

# from jaclang.plugin.default import JacFeatureDefaults,JacBuiltin,my_function  # noqa: E402

jac_import = JacFeature.jac_import

__all__ = [
    "jac_import",
    "lark",
    "mypy",
    "pluggy",
]
pm.register(JacFeatureDefaults)
pm.register(JacBuiltin)
# pm.register(my_function)
pm.load_setuptools_entrypoints("jac")
