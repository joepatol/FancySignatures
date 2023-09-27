import pytest
from typing import ContextManager
from contextlib import nullcontext as does_not_raise
from fancy_signatures.alias import check_alias_collisions, process_aliases


@pytest.mark.parametrize(
    "param_names, aliases, expectation",
    [
        pytest.param(["a", "b", "c"], ["c", "d"], pytest.raises(ValueError)),
        pytest.param(["a", "b", "c"], ["d", "d"], pytest.raises(ValueError)),
        pytest.param(["a", "b", "c"], ["d", "e"], does_not_raise()),
        pytest.param(["a", "b", "c"], ["d", None], does_not_raise()),
        pytest.param(["a", "b", "d"], ["d", None], pytest.raises(ValueError)),
    ],
)
def test__alias_collisions(param_names: list[str], aliases: list[str], expectation: ContextManager) -> None:
    with expectation:
        check_alias_collisions(param_names, aliases)


def test__process_aliases() -> None:
    r = process_aliases(
        {"param1": "alias1"},
        {
            "alias1": 10,
            "param2": 2,
        },
    )

    assert r == {"param1": 10, "param2": 2}


def test__process_aliases_none() -> None:
    r = process_aliases(
        {
            "param1": "alias1",
            "param2": None,
        },
        {
            "alias1": 10,
            "param2": 2,
        },
    )

    assert r == {"param1": 10, "param2": 2}
