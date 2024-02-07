# BigHat Coding Challenge

## Requirements

Probably not hard requirements, but the current versions I used in my environment. Hopefully Poetry is not a "special" package management system.

Python 3.11+
Pydantic 2.6.1+
Poetry 1.7.1+

## Installation

```
$ poetry install
```

## Run it

```
$ poetry run dag example.json
```

## Testing

```
$ poetry run pytest
```

or if you want to see `print()` outputs

```
$ poetry run pytest -s
```

It is difficult to test async operations where the desired outcome is a `print()` side effect. To handle more robust
testing I subclassed `DAGModel` to `DAGTestModel` and overrode the `vertex_run()` and `run()` functions to track and
store the time of `vertex_run()` executions. This allows me to not rely on `print()` statements and introspect the
`execution_times` attribute to ensure that the vertices are being visited in the correct order given the different
`edge` values.

This rough approximation _should_ be safe if the edge sleep values are in seconds, however due to the stochastic nature
of the underlying compute infrastructure, this approximation will likely fail if the edge values are in the microsecond range.

## Approach

I tried to keep it as simple as possible and not install extraneous packages (such as `pandas` or `networkx`) that may
have made the graph traversal more straightforward. As is, nothing other than Poetry and Pydantic are needed to build
and run the workflow engine. I also installed `ipython` to help with debugging.

### DAG Representation

I used a simple dict of dicts (or an adjacency matrix) to represent the DAG. For the example

```
{
    "A": {
        "start": true,
        "edges": {
            "B": 5,
            "C": 7
        }
    },
    "B": {
        "edges": {}
    },
    "C": {
        "edges": {}
    }
}
```

the resulting adjacency matrix would be

```
adjacency_matrix = {
    "A": {"B": 5, "C": 7},
    "B": {},
    "C": {},
}
```

I chose to remove the `start` information from the graph itself since theoretically you can begin the execution of
the DAG at any vertex and that can be parameterized. The value for the edges are the values of the inner dictionaries.
To get the value of the edge between vertices `A` and `B` you would do

```
> adjacency_matrix["A"]["B"]
5
```

### OOP

I decided to use an object oriented approach to implement the DAG and also create an abstract base class to allow
for extensibility in case different edge and vertex behavior is desired.

The `DAGBaseModel` class contains the class constructor method `from_dict()` as well as the `run()` method which
does a breadth first traversal of the graph and calls the `edge_run()` and `vertex_run()` methods for each vertex.

The concrete class needs to override the `edge_run()` and `vertex_run()` methods to add the desired business logic.
In this case it is to `sleep()` for a specified number of seconds before `print()`-ing the name of the vertex.
Inheritance allows us to decouple the DAG structure and traversal from the execution logic which makes things
clean and clear for a developer to understand.

### Async

Since vertex execution needs to happen in parallel, we need to use `async` to fire off all the `edge_run()` and
`vertex_run()` functions and then use `asyncio.gather()` to gather the results on completion.

## Commentary

The hardest part was testing the async execution of vertices based on the edge timing. I don't know of a great way
to `assert` stdout... perhaps capturing it all in `StringIO` and examining the contents, but feels really hacky. My
choice to use inherited classes was primarily to design the workflow runner _to spec_ while not encumbering it with
additional features that are only used for testing purposes.

## Todos

Things I didn't get to that probably make sense:

- DAG validation
  - I don't validate that the input json/dict is compliant or that there is always a single `start` vertex
- More thorough unit testing
  - I could probably make sure that `edge_run()` and `vertex_run()` are called the expected number of times
