class ValidationError(Exception):
    def __init__(self, message: str, param: str | list[str]) -> None:
        if isinstance(param, list):
            msg = f"Parameters '{param}' are invalid. {message}."
        else:
            msg = f"Parameter '{param}' is invalid. {message}."
        super().__init__(msg)


class TypeCastError(ValidationError):
    pass


class TypeValidationError(TypeError):
    pass


class ValidationErrorGroup(ExceptionGroup, ValidationError):
    pass
