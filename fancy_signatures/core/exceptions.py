class ValidationError(Exception):
    def __init__(self, message: str, param: str) -> None:
        super().__init__(f"Parameter '{param}' is invalid. {message}.")


class TypeCastError(ValidationError):
    pass


class TypeValidationError(TypeError):
    pass


class ValidationErrorGroup(ExceptionGroup, ValidationError):
    pass
