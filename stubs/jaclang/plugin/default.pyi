import types
from jaclang.compiler.constant import EdgeDir
from jaclang.core.construct import (
    Architype as Architype,
    DSFunc as DSFunc,
    EdgeAnchor as EdgeAnchor,
    EdgeArchitype as EdgeArchitype,
    GenericEdge as GenericEdge,
    JacTestCheck as JacTestCheck,
    NodeAnchor as NodeAnchor,
    NodeArchitype as NodeArchitype,
    ObjectAnchor as ObjectAnchor,
    Root as Root,
    WalkerAnchor as WalkerAnchor,
    WalkerArchitype as WalkerArchitype,
    root as root,
)
from jaclang.core.importer import jac_importer as jac_importer
from typing import Any, Callable, Optional, Type, TypeVar
import pluggy

__all__ = [
    "EdgeAnchor",
    "GenericEdge",
    "JacTestCheck",
    "NodeAnchor",
    "ObjectAnchor",
    "WalkerAnchor",
    "NodeArchitype",
    "EdgeArchitype",
    "WalkerArchitype",
    "Architype",
    "DSFunc",
    "root",
    "Root",
    "jac_importer",
    "T",
    "ArchBound",
]

T = TypeVar("T")
ArchBound = TypeVar("ArchBound", bound=Architype)
hookimpl = pluggy.HookimplMarker("jac")

class JacFeatureDefaults:
    @staticmethod
    def make_obj(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]: ...
    @staticmethod
    def make_node(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]: ...
    @staticmethod
    def make_edge(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]: ...
    @staticmethod
    def make_walker(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]: ...
    @staticmethod
    def jac_import(
        target: str, base_path: str, cachable: bool, override_name: Optional[str]
    ) -> Optional[types.ModuleType]: ...
    @staticmethod
    def create_test(test_fun: Callable) -> Callable: ...
    @staticmethod
    def run_test(filename: str) -> None: ...
    @staticmethod
    def elvis(op1: Optional[T], op2: T) -> T: ...
    @staticmethod
    def has_instance_default(gen_func: Callable[[], T]) -> T: ...
    @staticmethod
    def spawn_call(op1: Architype, op2: Architype) -> Architype: ...
    @staticmethod
    def report(expr: Any) -> Any: ...
    @staticmethod
    def ignore(
        walker: WalkerArchitype,
        expr: list[NodeArchitype | EdgeArchitype] | NodeArchitype | EdgeArchitype,
    ) -> bool: ...
    @staticmethod
    def visit_node(
        walker: WalkerArchitype,
        expr: list[NodeArchitype | EdgeArchitype] | NodeArchitype | EdgeArchitype,
    ) -> bool: ...
    @staticmethod
    def disengage(walker: WalkerArchitype) -> bool: ...
    @staticmethod
    def edge_ref(
        node_obj: NodeArchitype,
        dir: EdgeDir,
        filter_type: Optional[type],
        filter_func: Optional[Callable],
    ) -> list[NodeArchitype]: ...
    @staticmethod
    def connect(
        left: NodeArchitype | list[NodeArchitype],
        right: NodeArchitype | list[NodeArchitype],
        edge_spec: EdgeArchitype,
    ) -> NodeArchitype | list[NodeArchitype]: ...
    @staticmethod
    def disconnect(op1: Optional[T], op2: T, op: Any) -> T: ...
    @staticmethod
    def assign_compr(
        target: list[T], attr_val: tuple[tuple[str], tuple[Any]]
    ) -> list[T]: ...
    @staticmethod
    def get_root() -> Architype: ...
    @staticmethod
    def build_edge(
        edge_dir: EdgeDir,
        conn_type: Optional[Type[Architype]],
        conn_assign: Optional[tuple[tuple, tuple]],
    ) -> Architype: ...
