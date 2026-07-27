from engine.variable_engine import VariableEngine


class ConditionEngine:
    @staticmethod
    def contains(left, right, variables):
        left = VariableEngine.resolve(left, variables)
        right = VariableEngine.resolve(right, variables)

        return str(right) in str(left)

    @staticmethod
    def equals(left, right, variables):
        left = VariableEngine.resolve(left, variables)
        right = VariableEngine.resolve(right, variables)

        return str(left) == str(right)