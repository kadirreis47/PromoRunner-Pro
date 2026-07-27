from engine.action_if import ActionIf
from engine.context import ExecutionContext


ctx = ExecutionContext()
ctx.set("page_title", "Example Domain")
ctx.set("site", "CASIBOM")
ctx.set("empty_value", "")

tests = [
    {
        "if": {
            "operator": "contains",
            "left": "${page_title}",
            "right": "Example",
        }
    },
    {
        "if": {
            "operator": "not_contains",
            "left": "${page_title}",
            "right": "Google",
        }
    },
    {
        "if": {
            "operator": "equals",
            "left": "${site}",
            "right": "CASIBOM",
        }
    },
    {
        "if": {
            "operator": "not_equals",
            "left": "${site}",
            "right": "ROBIN",
        }
    },
    {
        "if": {
            "operator": "starts_with",
            "left": "${page_title}",
            "right": "Example",
        }
    },
    {
        "if": {
            "operator": "ends_with",
            "left": "${page_title}",
            "right": "Domain",
        }
    },
    {
        "if": {
            "operator": "exists",
            "left": "${site}",
        }
    },
    {
        "if": {
            "operator": "not_exists",
            "left": "${empty_value}",
        }
    },
]

for test in tests:
    print(ActionIf.should_execute(test, ctx))
