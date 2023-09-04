from typing import Any

from ..core.interface import TypeCaster
from .casters import register_handler


class StringTypeCaster(TypeCaster[str]):
    def validate(self, param_value: Any) -> bool:
        return isinstance(param_value, str)
    
    def cast(self, param_value: Any) -> str:
        return str(param_value)
    

class AnyTypeCaster(TypeCaster[Any]):
    def validate(self, _: Any) -> bool: return True
    def cast(self, param_value: Any) -> Any: return param_value
    

register_handler(type_hints=[str], handler=StringTypeCaster, strict=True)
register_handler(type_hints=[Any], handler=AnyTypeCaster, strict=True)
