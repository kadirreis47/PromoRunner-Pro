from engine.variable_engine import VariableEngine


variables = {
    "code": "BONUS250",
    "site": "CASIBOM",
}

print(
    VariableEngine.resolve(
        "Kod: ${code}",
        variables,
    )
)

print(
    VariableEngine.resolve(
        "Site: ${site}",
        variables,
    )
)