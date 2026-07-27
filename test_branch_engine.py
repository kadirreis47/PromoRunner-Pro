from engine.branch_engine import BranchEngine


def test_first_matching_branch() -> None:
    step = {
        "action": "branch",
        "branches": [
            {
                "name": "failed",
                "if": {
                    "operator": "equals",
                    "left": "${status}",
                    "right": "failed",
                },
                "steps": [{"action": "log", "message": "failed"}],
            },
            {
                "name": "approved",
                "if": {
                    "all": [
                        {
                            "operator": "equals",
                            "left": "${status}",
                            "right": "approved",
                        },
                        {
                            "operator": "contains",
                            "left": "${message}",
                            "right": "success",
                        },
                    ]
                },
                "steps": [{"action": "log", "message": "approved"}],
            },
        ],
        "default": [{"action": "log", "message": "unknown"}],
    }

    result = BranchEngine.select(
        step,
        {"status": "approved", "message": "promo success"},
    )

    assert result.matched is True
    assert result.branch_index == 1
    assert result.branch_name == "approved"
    assert result.steps[0]["message"] == "approved"


def test_default_branch() -> None:
    step = {
        "action": "branch",
        "branches": [
            {
                "name": "approved",
                "condition": {
                    "operator": "equals",
                    "left": "${status}",
                    "right": "approved",
                },
                "steps": [],
            }
        ],
        "else": {
            "name": "fallback",
            "steps": [{"action": "log", "message": "fallback"}],
        },
    }

    result = BranchEngine.select(step, {"status": "rejected"})

    assert result.matched is False
    assert result.branch_name == "fallback"
    assert result.steps[0]["message"] == "fallback"


def test_no_match_without_default() -> None:
    step = {
        "action": "branch",
        "cases": [
            {
                "if": {
                    "operator": "equals",
                    "left": "${status}",
                    "right": "approved",
                },
                "steps": [],
            }
        ],
    }

    result = BranchEngine.select(step, {"status": "rejected"})

    assert result.matched is False
    assert result.branch_name == "none"
    assert result.steps == []


if __name__ == "__main__":
    test_first_matching_branch()
    test_default_branch()
    test_no_match_without_default()
    print("BRANCH_ENGINE_TESTS_OK")
