import argparse
import json
import asyncio
from pathlib import Path

from .dag import DAGModel


async def async_main():
    parser = argparse.ArgumentParser(description="DAG")
    parser.add_argument("config", type=str, help="DAG config json file")
    args = parser.parse_args()

    with open(Path(args.config)) as f:
        config = json.load(f)
        dag = DAGModel.from_dict(config)
        await dag.run()


def main():
    asyncio.run(async_main())
