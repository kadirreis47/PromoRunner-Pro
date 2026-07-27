import asyncio

from engine.context import ExecutionContext
from engine.generic_handler import GenericHandler
from engine.loop_engine import LoopEngine


def execute(steps, initial=None):
    handler = GenericHandler({"site_name": "LOOP_TEST", "steps": steps})
    context = ExecutionContext()
    for key, value in (initial or {}).items():
        context.set(key, value)
    asyncio.run(
        handler._execute_steps(
            page=None,
            steps=steps,
            context=context,
            timeout=1000,
        )
    )
    return context


def test_repeat() -> None:
    context = execute(
        [
            {"action": "set", "name": "counter", "value": 0},
            {
                "action": "repeat",
                "times": 4,
                "index_as": "i",
                "steps": [
                    {"action": "increment", "name": "counter", "by": 1}
                ],
            },
        ]
    )
    assert context.get("counter") == 4
    assert not context.has("i")


def test_for_each_continue_and_break() -> None:
    context = execute(
        [
            {"action": "set", "name": "visited", "value": 0},
            {
                "action": "for_each",
                "items": ["a", "skip", "b", "stop", "c"],
                "item_as": "item",
                "steps": [
                    {
                        "action": "branch",
                        "branches": [
                            {
                                "name": "skip",
                                "if": {
                                    "operator": "equals",
                                    "left": "${item}",
                                    "right": "skip",
                                },
                                "steps": [{"action": "continue"}],
                            },
                            {
                                "name": "stop",
                                "if": {
                                    "operator": "equals",
                                    "left": "${item}",
                                    "right": "stop",
                                },
                                "steps": [{"action": "break"}],
                            },
                        ],
                    },
                    {"action": "increment", "name": "visited", "by": 1},
                ],
            },
        ]
    )
    assert context.get("visited") == 2
    assert not context.has("item")


def test_while() -> None:
    context = execute(
        [
            {"action": "set", "name": "number", "value": 0},
            {
                "action": "while",
                "condition": {
                    "operator": "less_than",
                    "left": "${number}",
                    "right": 5,
                },
                "max_iterations": 10,
                "steps": [
                    {"action": "increment", "name": "number", "by": 1}
                ],
            },
        ]
    )
    assert context.get("number") == 5


def test_nested_loop_breaks_nearest_loop() -> None:
    context = execute(
        [
            {"action": "set", "name": "total", "value": 0},
            {
                "action": "repeat",
                "times": 3,
                "steps": [
                    {
                        "action": "repeat",
                        "times": 5,
                        "steps": [
                            {"action": "increment", "name": "total"},
                            {"action": "break"},
                        ],
                    }
                ],
            },
        ]
    )
    assert context.get("total") == 3


def test_parser_and_raw_list_variable() -> None:
    variables = {"codes": ["A", "B"]}
    spec = LoopEngine.parse(
        {
            "action": "loop",
            "type": "for_each",
            "items": "${codes}",
            "steps": [],
        },
        variables,
    )
    assert spec.items == ["A", "B"]


if __name__ == "__main__":
    test_repeat()
    test_for_each_continue_and_break()
    test_while()
    test_nested_loop_breaks_nearest_loop()
    test_parser_and_raw_list_variable()
    print("LOOP_ENGINE_TESTS_OK")
