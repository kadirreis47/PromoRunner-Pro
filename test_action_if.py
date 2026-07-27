from engine.context import ExecutionContext
from engine.action_if import ActionIf

ctx = ExecutionContext()
ctx.set("page_title", "Example Domain")
ctx.set("site", "CASIBOM")

step1 = {
    "if": {
        "operator": "contains",
        "left": "${page_title}",
        "right": "Example"
    }
}

step2 = {
    "if": {
        "operator": "equals",
        "left": "${site}",
        "right": "CASIBOM"
    }
}

step3 = {
    "if": {
        "operator": "equals",
        "left": "${site}",
        "right": "ROBIN"
    }
}

print(ActionIf.should_execute(step1, ctx))
print(ActionIf.should_execute(step2, ctx))
print(ActionIf.should_execute(step3, ctx))