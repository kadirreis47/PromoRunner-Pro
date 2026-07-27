from engine.context import ExecutionContext

ctx = ExecutionContext()

ctx.set("code", "BONUS250")
ctx.set("site", "CASIBOM")

print(ctx.get("code"))
print(ctx.get("site"))
print(ctx.all())