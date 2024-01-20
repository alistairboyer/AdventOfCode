from typing import List, Dict, Tuple, Set, Iterator, Sequence, Collection, Optional, Any
import io


def debug(*args: Any, **kwargs: Any) -> None:
    pass


class Graph:
    """
    A non-directional graph of connected nodes.
    Index the created object with square brackets to access the nodes.
    Iterating the object iterates through it's nodes.
    """

    def __init__(self, nodes_data: Collection[str]) -> None:
        self.nodes: Dict[str, "Node"] = dict()
        for node_data in nodes_data:
            if not node_data:
                continue
            self.add_node(node_data)

    def __getitem__(self, key: str) -> "Node":
        return self.nodes[key]

    def __iter__(self) -> Iterator["Node"]:
        yield from self.nodes.values()

    def get_or_create_node(self, key: str) -> "Node":
        """
        Get a node from the graph or if it doesn not exist creat the node and return it.
        """
        node = self.nodes.get(key, None)
        if node is None:
            node = Node(key)
            self.nodes[key] = node
        return node

    def add_node(self, node_data_str: str) -> None:
        """
        Add a node to the network using a str representation as parsed by Node.parse_str.
        """
        [name, links] = Node.parse_str(node_data_str)
        node = self.get_or_create_node(name)
        for link_str in links:
            linked_node = self.get_or_create_node(link_str)
            linked_node.new_link(node)
            node.new_link(linked_node)

    def to_DOT(self) -> str:
        """
        Convert object to DOT format for e.g. graphviz.
        """
        output = io.StringIO()
        output.write("strict graph {\n")
        for node in self.nodes.values():
            output.write(f"  {node.to_DOT()}\n")
        output.write("}\n")
        return output.getvalue()

    def find_node_group_with_n_links(self, n: int) -> Optional["NodeGroup"]:
        """
        Find a node group that is connected to the rest of the nodes by n conections or returns None.
        """
        n = int(n)
        debug("  Looking for node group with", n, "links starting from:", end=" ")
        for node in self:
            debug(node.name, end="; ")
            ng = NodeGroup()
            ng.add_node(node)
            while True:
                if ng.nnodes() >= len(self.nodes):
                    break
                for node in list(ng.linked_nodes):
                    ng.add_node(node)
                    if ng.nlinks() == n:
                        debug()
                        return ng
        return None


class NodeGroup:
    """
    A group of nodes that have been folded together along edges.
    """

    def __init__(self) -> None:
        self.nodes: List["Node"] = list()
        self.linked_nodes: List["Node"] = list()

    def nnodes(self) -> int:
        """
        Number of nodes.
        """
        return len(self.nodes)

    def nlinks(self) -> int:
        """
        Number of linked nodes.
        """
        return len(self.linked_nodes)

    def links(self) -> List[Tuple["Node", "Node"]]:
        """
        A list of links that need to be cut in the format
        of a tuple with the from node and the to node.
        """
        node_set = set(self.nodes)
        links = list()
        for linked_node in self.linked_nodes:
            for node in set(linked_node.linked_nodes).intersection(node_set):
                links.append((node, linked_node))
        return links

    def add_node(self, *nodes: "Node") -> None:
        """
        Add nodes to the node group.
        """
        for node in nodes:
            if node in self.nodes:
                continue
            # add node to list of nodes
            self.nodes.append(node)
            # get links from nodes
            self.linked_nodes += node.linked_nodes
        # remove any internal links
        self.linked_nodes = [
            node for node in self.linked_nodes if node not in self.nodes
        ]


class Node:
    def __init__(self, name: str) -> None:
        self.name: str = str(name)
        self.linked_nodes: Set["Node"] = set()

    def __repr__(self) -> str:
        return f"Node[{self.name}]"

    def __str__(self) -> str:
        return self.name

    def new_link(self, *node: "Node") -> None:
        """
        Add new links.
        """
        self.linked_nodes.update({*node})

    @staticmethod
    def parse_str(node_data_str: str) -> Tuple[str, List[str]]:
        """
        Parse the Advent of Code str input into a node name and list of names of linked nodes.
        """
        [name, links] = node_data_str.split(": ")
        return name, links.split(" ")

    def nlinks(self) -> int:
        """
        Number of linked nodes.
        """
        return len(self.linked_nodes)

    def nnodes(self) -> int:
        """
        Number of nodes. Defined as 1.
        """
        return 1

    def to_DOT(self) -> str:
        """
        A str representation of the node and its connections in DOT format.
        """
        return f"""{self.name} -- {{{" ".join(node.name for node in self.linked_nodes)}}}"""


def to_DOT(data: Sequence[str]) -> str:
    """
    Convert the raw Advent of Code 2023 day 25 input to DOT strict graph.
    """
    output = io.StringIO()
    output.write("strict graph {\n")
    for line in data:
        if not line:
            continue
        line = line.replace(": ", " -- {")
        output.write(f"  {line}}}\n")
    output.write("}\n")
    return output.getvalue()


def go(name: str, data: str, print_dot: bool = False) -> None:
    network = Graph(data.splitlines())
    if print_dot:
        print(network.to_DOT())
        exit()
    debug(name, "Part 1")
    debug("  Network loaded with", len(network.nodes), "nodes.")
    ng = network.find_node_group_with_n_links(3)
    if ng is None:
        debug("  Could not find solution.")
        debug()
        return
    b = len(network.nodes) - ng.nnodes()
    debug("  Links cut", ng.links())
    debug("  Network split into:", ng.nnodes(), b, f"({ng.nnodes()*b})")
    debug()


if __name__ == "__main__":
    import sys

    from DataSample import DAY_25 as SAMPLE

    go("Sample", SAMPLE, "dot" in sys.argv)

    try:
        from DataFull_ import DAY_25 as DATA

        go("Full Data", DATA)

    except ImportError:
        pass
