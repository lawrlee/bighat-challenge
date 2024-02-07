import abc
import asyncio
from typing import Self, Dict
from pydantic import BaseModel


class DAGBaseModel(BaseModel, abc.ABC):
    """This is the Abstract Base Class for the DAGModel. The DAG is represented
    as an adjacency matrix implemented as a dictionary of dictionaries. The keys
    of the outer dictionary are the vertex ids and the keys of the inner dictionaries
    are the ids of the vertices that the outer vertex is connected to. The values of
    the inner dictionaries are the weights of the edges between the vertices.
    The start attribute is the id of the vertex that the DAG should start from.

    There are two abstract methods that must be implemented by the concrete class:
        - `edge_run()`
        - `vertex_run()`

    The concrete class determines the behavior of the `edge_run()` and `vertex_run()`
    methods. The `run()` method is a recursive method that traverses the DAG starting from
    the vertex specified by the `start` attribute. For each vertex to be visited, the
    `edge_run()` and `vertex_run()` methods are called.

    The `from_dict()` method is a class method that parses a dictionary specification of
    the DAG and returns an instance of the concrete class.
    """

    adjacency_matrix: Dict[str, Dict[str, int]]
    start: str

    @classmethod
    def from_dict(cls, config: dict) -> Self:
        """This function parses the DAG configuration specification and returns an
        instance of the concrete class with the adjacency matrix and start attributes
        set.

        Args:
            config (dict): The configuration specification of the DAG

        Returns:
            Self: An instance of the concrete class
        """
        adjacency_matrix = {}
        start = None
        for id, vertex in config.items():
            if id not in adjacency_matrix:
                adjacency_matrix[id] = {}
            edges = vertex["edges"]
            if vertex.get("start", False):
                start = id
            for edge_id in edges:
                adjacency_matrix[id][edge_id] = edges[edge_id]
        return cls(adjacency_matrix=adjacency_matrix, start=start)

    @abc.abstractmethod
    async def edge_run(self, value: int = 0):
        pass

    @abc.abstractmethod
    async def vertex_run(self, id: str):
        pass

    async def run(self, start: str = None, edge: int = 0):
        """The main execution method for the DAG. This method takes a starting vertex
        and an edge value and runs the `edge_run()` and `vertex_run()` methods.

        Args:
            start (str, optional): The starting vertex. If None, the start attribute
            is used. Defaults to None.
            edge (int, optional): The value of the input edge. Defaults to 0 if we
            are starting from the root vertex or if the edge value is not specified.
        """
        if start is None:
            start = self.start
        await self.edge_run(edge)
        await self.vertex_run(start)

        await asyncio.gather(
            *[
                self.run(
                    start=child_id,
                    edge=child_edge,
                )
                for child_id, child_edge in self.adjacency_matrix[start].items()
            ]
        )


class DAGModel(DAGBaseModel):
    """This is the concrete class that implements the `edge_run()` and `vertex_run()`
    methods as detailed in the challenge documentation. As specified, the child vertices
    of a parent vertex should wait `value` seconds before being visited. Each vertex
    visited should print its `id` to the console.
    """

    async def edge_run(self, value: int = 0):
        await asyncio.sleep(value)

    async def vertex_run(self, id: str):
        print(id)
