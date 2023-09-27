from typing import Any, Sequence


def check_alias_collisions(param_names: Sequence[str], aliases: Sequence[str | None]) -> None:
    all = list(param_names) + [alias for alias in aliases if alias is not None]

    if len(set(all)) != len(all):
        raise ValueError("Aliases and argument names should be unique")


def process_aliases(aliases: dict[str, str | None], kwargs: dict[str, Any]) -> dict[str, Any]:
    processed_kwargs = kwargs.copy()

    for name, alias in aliases.items():
        if alias is not None and kwargs.get(alias):
            processed_kwargs[name] = kwargs[alias]
            del processed_kwargs[alias]
        elif kwargs.get(name):
            processed_kwargs[name] = kwargs[name]

    return processed_kwargs
