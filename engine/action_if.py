from engine.condition_engine import ConditionEngine


class ActionIf:
    @staticmethod
    def should_execute(step, context):
        condition = step.get("if")

        if not condition:
            return True

        return ConditionEngine.evaluate_condition(
            condition=condition,
            variables=context.all(),
        )
