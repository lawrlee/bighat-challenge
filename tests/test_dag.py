import pytest
import time
from bighat_challenge.dag import DAGModel
from typing import Dict

DAG_CONFIG_1 = {
    "A": {"start": True, "edges": {"B": 5, "C": 7}},
    "B": {"edges": {}},
    "C": {"edges": {}},
}
DAG_EXPECTED_ORDER_1 = ["A", "B", "C"]


DAG_CONFIG_2 = {
    "A": {"start": True, "edges": {"B": 5, "C": 1}},
    "B": {"edges": {}},
    "C": {"edges": {"D": 1}},
    "D": {"edges": {"E": 1}},
    "E": {"edges": {"F": 1}},
    "F": {"edges": {}},
}
DAG_EXPECTED_ORDER_2 = ["A", "C", "D", "E", "F", "B"]


DAG_CONFIG_3 = {
    "A": {"start": True, "edges": {"B": 3, "C": 1}},
    "B": {"edges": {"G": 2}},
    "C": {"edges": {"D": 1}},
    "D": {"edges": {"E": 2}},
    "E": {"edges": {"F": 2}},
    "F": {"edges": {}},
    "G": {"edges": {}},
}
DAG_EXPECTED_ORDER_3 = ["A", "C", "D", "B", "E", "G", "F"]

BAD_DAG_CONFIG_1 = {
    "A": {"start": False, "edges": {"B": 5, "C": 7}},
    "B": {"edges": {}},
    "C": {"edges": {}},
}


class DAGTestModel(DAGModel):
    """This is a subclass of the DAGModel that is used for testing. It wraps the `run()`
    method to track the start time and wraps the `vertex_run()` method to track the time
    of each `vertex_run()` call. We add the `execution_time` and `start_time` attributes
    to facilitate this tracking.

    Args:
        DAGModel (_type_): _description_
    """

    execution_time: Dict[str, float] = {}
    start_time: float = None

    async def run(self, start: str = None, edge: int = 0):
        """Save `self.start_time` if not already set and call the parent `run()` method."""
        if not self.start_time:
            self.start_time = time.perf_counter()
        await super().run(start, edge)

    async def vertex_run(self, value: str):
        """Track the execution time of each `vertex_run()` call rounded to the nearest second."""
        elapsed = time.perf_counter() - self.start_time
        await super().vertex_run(value)
        self.execution_time[value] = round(elapsed)


def test_create_dag_model():
    dag = DAGModel.from_dict(config=DAG_CONFIG_1)
    assert isinstance(dag, DAGModel)
    assert isinstance(dag.adjacency_matrix, dict)
    assert isinstance(dag.start, str)
    assert dag.start == "A"
    assert dag.adjacency_matrix == {
        "A": {"B": 5, "C": 7},
        "B": {},
        "C": {},
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "config,expected_order",
    [
        (DAG_CONFIG_1, DAG_EXPECTED_ORDER_1),
        (DAG_CONFIG_2, DAG_EXPECTED_ORDER_2),
        (DAG_CONFIG_3, DAG_EXPECTED_ORDER_3),
    ],
)
async def test_run_dag_model(config, expected_order):
    dag = DAGTestModel.from_dict(config=config)
    await dag.run()

    print(dag.execution_time)
    ordered_nodes = sorted(dag.execution_time.items(), key=lambda x: x[1])
    assert [node[0] for node in ordered_nodes] == expected_order
