from engine.action_if import ActionIf
from engine.context import ExecutionContext


ctx = ExecutionContext()
ctx.set("page_title", "Example Domain")
ctx.set("site", "CASIBOM")
ctx.set("promo_code", "TEST123")

tests = [
    {
        "if": {
            "all": [
                {
                    "operator": "contains",
                    "left": "${page_title}",
                    "right": "Example",
                },
                {
                    "operator": "equals",
                    "left": "${site}",
                    "right": "CASIBOM",
                },
            ]
        }
    },
    {
        "if": {
            "any": [
                {
                    "operator": "equals",
                    "left": "${site}",
                    "right": "ROBIN",
                },
                {
                    "operator": "equals",
                    "left": "${promo_code}",
                    "right": "TEST123",
                },
            ]
        }
    },
    {
        "if": {
            "not": {
                "operator": "equals",
                "left": "${site}",
                "right": "ROBIN",
            }
        }
    },
    {
        "if": {
            "all": [
                {
                    "operator": "equals",
                    "left": "${site}",
                    "right": "CASIBOM",
                },
                {
                    "any": [
                        {
                            "operator": "equals",
                            "left": "${promo_code}",
                            "right": "WRONG",
                        },
                        {
                            "operator": "contains",
                            "left": "${page_title}",
                            "right": "Domain",
                        },
                    ]
                },
            ]
        }
    },
    {
        "if": {
            "all": [
                {
                    "operator": "equals",
                    "left": "${site}",
                    "right": "CASIBOM",
                },
                {
                    "operator": "equals",
                    "left": "${promo_code}",
                    "right": "WRONG",
                },
            ]
        }
    },
]

for test in tests:
    print(ActionIf.should_execute(test, ctx))
