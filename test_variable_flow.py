from engine.context import ExecutionContext
from engine.variable_engine import VariableEngine

ctx = ExecutionContext()

ctx.set("promo_code", "TEST123")
ctx.set("site", "CASIBOM")

ctx.set(
    "message",
    VariableEngine.resolve(
        "Kod: ${promo_code} | Site: ${site}",
        ctx.all(),
    ),
)

ctx.set(
    "url",
    VariableEngine.resolve(
        "https://${site}.com",
        ctx.all(),
    ).lower(),
)

print(ctx.get("message"))
print(ctx.get("url"))