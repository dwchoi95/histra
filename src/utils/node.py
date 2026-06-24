class Node:
    __slots__ = ("name", "children", "node")

    def __init__(self, name, children, node):
        self.name = name
        self.children = children
        self.node = node