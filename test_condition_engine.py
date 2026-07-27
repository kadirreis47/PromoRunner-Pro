from engine.condition_engine import ConditionEngine

variables = {
    "title": "Example Domain",
    "site": "CASIBOM"
}

print(
    ConditionEngine.contains(
        "${title}",
        "Example",
        variables
    )
)

print(
    ConditionEngine.equals(
        "${site}",
        "CASIBOM",
        variables
    )
)

print(
    ConditionEngine.equals(
        "${site}",
        "ROBIN",
        variables
    )
)