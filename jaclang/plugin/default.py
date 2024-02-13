"""Jac Language Features."""

from __future__ import annotations

import os
import types
from dataclasses import field
from functools import wraps
from typing import Any, Callable, Optional, Type

from jaclang.compiler.absyntree import Module
from jaclang.compiler.constant import EdgeDir
from jaclang.core.construct import (
    Architype,
    DSFunc,
    EdgeAnchor,
    EdgeArchitype,
    GenericEdge,
    JacTestCheck,
    NodeAnchor,
    NodeArchitype,
    ObjectAnchor,
    Root,
    WalkerAnchor,
    WalkerArchitype,
    root,
)
from jaclang.core.importer import jac_importer
from jaclang.plugin.feature import JacFeature as Jac
from jaclang.plugin.spec import T

# from jaclang.core.jacbuiltins import dotgen


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
]


hookimpl = pluggy.HookimplMarker("jac")


class JacFeatureDefaults:
    """Jac Feature."""

    pm = pluggy.PluginManager("jac")

    @staticmethod
    @hookimpl
    def make_architype(
        cls: type,
        arch_base: Type[Architype],
        on_entry: list[DSFunc],
        on_exit: list[DSFunc],
    ) -> Type[Architype]:
        """Create a new architype."""
        for i in on_entry + on_exit:
            i.resolve(cls)
        if not issubclass(cls, arch_base):
            cls = type(cls.__name__, (cls, arch_base), {})
        cls._jac_entry_funcs_ = on_entry  # type: ignore
        cls._jac_exit_funcs_ = on_exit  # type: ignore
        inner_init = cls.__init__  # type: ignore

        @wraps(inner_init)
        def new_init(self: Architype, *args: object, **kwargs: object) -> None:
            inner_init(self, *args, **kwargs)
            arch_base.__init__(self)

        cls.__init__ = new_init  # type: ignore
        return cls

    @staticmethod
    @hookimpl
    def make_obj(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]:
        """Create a new architype."""

        def decorator(cls: Type[Architype]) -> Type[Architype]:
            """Decorate class."""
            cls = Jac.make_architype(
                cls=cls, arch_base=Architype, on_entry=on_entry, on_exit=on_exit
            )
            return cls

        return decorator

    @staticmethod
    @hookimpl
    def make_node(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]:
        """Create a obj architype."""

        def decorator(cls: Type[Architype]) -> Type[Architype]:
            """Decorate class."""
            cls = Jac.make_architype(
                cls=cls, arch_base=NodeArchitype, on_entry=on_entry, on_exit=on_exit
            )
            return cls

        return decorator

    @staticmethod
    @hookimpl
    def make_edge(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]:
        """Create a edge architype."""

        def decorator(cls: Type[Architype]) -> Type[Architype]:
            """Decorate class."""
            cls = Jac.make_architype(
                cls=cls, arch_base=EdgeArchitype, on_entry=on_entry, on_exit=on_exit
            )
            return cls

        return decorator

    @staticmethod
    @hookimpl
    def make_walker(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]:
        """Create a walker architype."""

        def decorator(cls: Type[Architype]) -> Type[Architype]:
            """Decorate class."""
            cls = Jac.make_architype(
                cls=cls, arch_base=WalkerArchitype, on_entry=on_entry, on_exit=on_exit
            )
            return cls

        return decorator

    @staticmethod
    @hookimpl
    def jac_import(
        target: str,
        base_path: str,
        cachable: bool,
        override_name: Optional[str],
        mod_bundle: Optional[Module],
    ) -> Optional[types.ModuleType]:
        """Core Import Process."""
        result = jac_importer(
            target=target,
            base_path=base_path,
            cachable=cachable,
            override_name=override_name,
            mod_bundle=mod_bundle,
        )
        return result

    @staticmethod
    @hookimpl
    def create_test(test_fun: Callable) -> Callable:
        """Create a new test."""

        def test_deco() -> None:
            test_fun(JacTestCheck())

        test_deco.__name__ = test_fun.__name__
        JacTestCheck.add_test(test_deco)

        return test_deco

    @staticmethod
    @hookimpl
    def run_test(filename: str) -> bool:
        """Run the test suite in the specified .jac file.

        :param filename: The path to the .jac file.
        """
        if filename.endswith(".jac"):
            base, mod_name = os.path.split(filename)
            base = base if base else "./"
            mod_name = mod_name[:-4]
            JacTestCheck.reset()
            Jac.jac_import(target=mod_name, base_path=base)
            JacTestCheck.run_test()
        else:
            print("Not a .jac file.")
        return True

    @staticmethod
    @hookimpl
    def elvis(op1: Optional[T], op2: T) -> T:
        """Jac's elvis operator feature."""
        return ret if (ret := op1) is not None else op2

    @staticmethod
    @hookimpl
    def has_instance_default(gen_func: Callable[[], T]) -> T:
        """Jac's has container default feature."""
        return field(default_factory=lambda: gen_func())

    @staticmethod
    @hookimpl
    def spawn_call(op1: Architype, op2: Architype) -> bool:
        """Jac's spawn operator feature."""
        if isinstance(op1, WalkerArchitype):
            op1._jac_.spawn_call(op2)
        elif isinstance(op2, WalkerArchitype):
            op2._jac_.spawn_call(op1)
        else:
            raise TypeError("Invalid walker object")
        return True

    @staticmethod
    @hookimpl
    def report(expr: Any) -> Any:  # noqa: ANN401
        """Jac's report stmt feature."""

    @staticmethod
    @hookimpl
    def ignore(
        walker: WalkerArchitype,
        expr: list[NodeArchitype | EdgeArchitype] | NodeArchitype | EdgeArchitype,
    ) -> bool:
        """Jac's ignore stmt feature."""
        return walker._jac_.ignore_node(expr)

    @staticmethod
    @hookimpl
    def visit_node(
        walker: WalkerArchitype,
        expr: list[NodeArchitype | EdgeArchitype] | NodeArchitype | EdgeArchitype,
    ) -> bool:
        """Jac's visit stmt feature."""
        if isinstance(walker, WalkerArchitype):
            return walker._jac_.visit_node(expr)
        else:
            raise TypeError("Invalid walker object")

    @staticmethod
    @hookimpl
    def disengage(walker: WalkerArchitype) -> bool:  # noqa: ANN401
        """Jac's disengage stmt feature."""
        walker._jac_.disengage_now()
        return True

    @staticmethod
    @hookimpl
    def edge_ref(
        node_obj: NodeArchitype | list[NodeArchitype],
        dir: EdgeDir,
        filter_type: Optional[type],
        filter_func: Optional[Callable[[list[EdgeArchitype]], list[EdgeArchitype]]],
    ) -> list[NodeArchitype]:
        """Jac's apply_dir stmt feature."""
        if isinstance(node_obj, NodeArchitype):
            return node_obj._jac_.edges_to_nodes(dir, filter_type, filter_func)
        elif isinstance(node_obj, list):
            connected_nodes = []
            for node in node_obj:
                connected_nodes.extend(
                    node._jac_.edges_to_nodes(dir, filter_type, filter_func)
                )
            return list(set(connected_nodes))
        else:
            raise TypeError("Invalid node object")

    @staticmethod
    @hookimpl
    def connect(
        left: NodeArchitype | list[NodeArchitype],
        right: NodeArchitype | list[NodeArchitype],
        edge_spec: Callable[[], EdgeArchitype],
    ) -> NodeArchitype | list[NodeArchitype]:
        """Jac's connect operator feature.

        Note: connect needs to call assign compr with tuple in op
        """
        left = [left] if isinstance(left, NodeArchitype) else left
        right = [right] if isinstance(right, NodeArchitype) else right
        for i in left:
            for j in right:
                i._jac_.connect_node(j, edge_spec())
        return left

    @staticmethod
    @hookimpl
    def disconnect(
        left: NodeArchitype | list[NodeArchitype],
        right: NodeArchitype | list[NodeArchitype],
        dir: EdgeDir,
        filter_type: Optional[type],
        filter_func: Optional[Callable[[list[EdgeArchitype]], list[EdgeArchitype]]],
    ) -> bool:  # noqa: ANN401
        """Jac's disconnect operator feature."""
        disconnect_occurred = False
        left = [left] if isinstance(left, NodeArchitype) else left
        right = [right] if isinstance(right, NodeArchitype) else right
        for i in left:
            for j in right:
                edge_list: list[EdgeArchitype] = [*i._jac_.edges]
                if filter_type:
                    edge_list = [e for e in edge_list if isinstance(e, filter_type)]
                edge_list = filter_func(edge_list) if filter_func else edge_list
                for e in edge_list:
                    if (
                        e._jac_.target
                        and e._jac_.source
                        and (not filter_type or isinstance(e, filter_type))
                    ):
                        if (
                            dir in ["OUT", "ANY"]
                            and i._jac_.obj == e._jac_.source
                            and e._jac_.target == j._jac_.obj
                        ):
                            e._jac_.detach(i._jac_.obj, e._jac_.target)
                            disconnect_occurred = True
                        if (
                            dir in ["IN", "ANY"]
                            and i._jac_.obj == e._jac_.target
                            and e._jac_.source == j._jac_.obj
                        ):
                            e._jac_.detach(i._jac_.obj, e._jac_.source)
                            disconnect_occurred = True
        return disconnect_occurred

    @staticmethod
    @hookimpl
    def assign_compr(
        target: list[T], attr_val: tuple[tuple[str], tuple[Any]]
    ) -> list[T]:
        """Jac's assign comprehension feature."""
        for obj in target:
            attrs, values = attr_val
            for attr, value in zip(attrs, values):
                setattr(obj, attr, value)
        return target

    @staticmethod
    @hookimpl
    def get_root() -> Architype:
        """Jac's assign comprehension feature."""
        return root

    @staticmethod
    @hookimpl
    def build_edge(
        is_undirected: bool,
        conn_type: Optional[Type[EdgeArchitype]],
        conn_assign: Optional[tuple[tuple, tuple]],
    ) -> Callable[[], EdgeArchitype]:
        """Jac's root getter."""
        conn_type = conn_type if conn_type else GenericEdge

        def builder() -> EdgeArchitype:
            edge = conn_type()
            edge._jac_.is_undirected = is_undirected
            if conn_assign:
                for fld, val in zip(conn_assign[0], conn_assign[1]):
                    if hasattr(edge, fld):
                        setattr(edge, fld, val)
                    else:
                        raise ValueError(f"Invalid attribute: {fld}")
            return edge

        return builder


class JacBuiltin:
    """Jac Builtins."""

    @staticmethod
    @hookimpl
    def dotgen(node: NodeArchitype, radius: int) -> str:
        """Print the dot graph."""
        full = bool(radius)
        node = node or root._jac_
        visited_nodes: set[NodeArchitype] = set()
        connections: set[tuple[NodeAnchor, NodeAnchor, EdgeArchitype]] = set()
        unique_node_id_dict = {}

        def generate_unique_node_id(node: NodeArchitype, idx: int) -> str:
            """Generate a unique node ID for the given node."""
            unique_node_id_dict[node] = str(idx)
            return f'{idx} [label="{node.obj}"];\n'

        def collect_node_connections(
            current_node: NodeAnchor,
            visited_nodes: set,
            connections: set,
            depth: int,
        ) -> None:
            """Nodes and edges representing the graph are collected in visited_nodes and connections."""
            if full and depth > radius:
                return
            if current_node not in visited_nodes:
                visited_nodes.add((current_node))
                for edge_ in current_node.edges:
                    if edge_._jac_ is not None and edge_._jac_.target is not None:
                        target = edge_._jac_.target
                        print(type(edge_))
                        print(type(target._jac_))
                        connections.add(((current_node), (target._jac_), edge_))
                        collect_node_connections(
                            target._jac_, visited_nodes, connections, depth + 1
                        )

        if node is not None:
            collect_node_connections(node, visited_nodes, connections, 0)
        dot_content = 'digraph {\nnode [style="filled", shape="ellipse", fillcolor="invis", fontcolor="black"];\n'
        dot_content += "".join(
            generate_unique_node_id(node, idx) for idx, node in enumerate(visited_nodes)
        )
        dot_content += 'edge [color="gray", style="solid"];\n'
        for source, target, edge in set(connections):
            source_node = unique_node_id_dict.get(source)
            target_node = unique_node_id_dict.get(target)

            if source != target and source_node and target_node:
                dot_content += (
                    f"{source_node} -> {target_node}"
                    f' [label="{edge.__class__.__name__}"];\n'
                )

        # if dot_file:
        #     with open(dot_file, "w") as f:
        #         f.write(dot_content + "}")
        return dot_content + "}"
        # return   len(dot_content)


# @hookimpl
# def my_function(arg1, arg2):
#     # Your function logic here
#     print("kukkuvaaa kokkaaaa")
