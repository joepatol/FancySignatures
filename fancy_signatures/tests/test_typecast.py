import pytest
from fancy_signatures.typecasting.factory import typecaster_factory
from fancy_signatures.core.exceptions import TypeValidationError



def test__strict_basic_type() -> None:
    caster = typecaster_factory(int)
    
    with pytest.raises(TypeValidationError):
        caster("10", True)
    
    
def test__strict_list_generic_alias() -> None:
    caster = typecaster_factory(list[int])
    
    with pytest.raises(TypeValidationError):
        caster(("a", "b"), True)

    with pytest.raises(TypeError):
        caster([1, "2"], True)


def test__strict_dict_generic_alias() -> None:
    caster = typecaster_factory(dict[str, float])
    caster({"a": 1.0}, True)
    
    with pytest.raises(TypeValidationError):
        caster({"a", 1}, True)
