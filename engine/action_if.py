from engine.condition_engine import ConditionEngine


class ActionIf:
    @staticmethod
    def should_execute(step, context):
        condition = step.get("if")

        if not condition:
            return True

        operator = condition.get("operator")

        if operator == "contains":
            return ConditionEngine.contains(
                condition["left"],
                condition["right"],
                context.all(),
            )

        if operator == "equals":
            return ConditionEngine.equals(
                condition["left"],
                condition["right"],
                context.all(),
            )

        return False