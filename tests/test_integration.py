from dataclasses import dataclass

from fancy_signatures import validate, argument
from fancy_signatures.validation.validators import GE, MaxLength
from fancy_signatures.exceptions import ValidationErrorGroup
from fancy_signatures.default import EmptyList


@validate(lazy=True)
@dataclass
class Course:
    name: str
    cost: float = argument(validators=[GE(0)], default=EmptyList)


@validate(lazy=True)
@dataclass
class Student:
    name: str
    age: int = argument(validators=[GE(0)])
    courses: list[Course] = argument(alias="course_ids", default=EmptyList)


@validate(lazy=True)
class ClassRoom:
    def __init__(
        self, name: str = argument(validators=[MaxLength(2)]), capacity: int = argument(validators=[GE(0)], alias="cap")
    ) -> None:
        self.name = name
        self.capacity = capacity

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ClassRoom):
            raise NotImplementedError()
        return self.name == __value.name and self.capacity == __value.capacity


@validate(lazy=True)
def load_students(
    budget: float = argument(validators=[GE(0)]),
    students: list[Student] = argument(alias="student_info_"),
    classrooms: list[ClassRoom] = argument(alias="rooms"),
) -> tuple[float, list[Student], list[ClassRoom]]:
    return budget, students, classrooms


INPUT_DATA_OK = {
    "budget": "125000",
    "rooms": [
        {"name": "1A", "capacity": "5"},
        {"name": "1B", "capacity": 3.0},
        {"name": "2A", "cap": "10"},
    ],
    "student_info_": [
        {"name": "Pete", "age": 27, "courses": [{"name": "a", "cost": "1.2"}]},
        {"name": "Sarah", "age": "25", "course_ids": [{"name": "b", "cost": "11.2"}]},
    ],
}


INPUT_DATA_NOT_OK = {
    "budget": "125000",
    "rooms": [
        {"name": "1AA", "capacity": "5"},
        {"name": "1B", "capacity": -3.0},
        {"name": "2A", "cap": "10"},
    ],
    "student_info_": [
        {"name": "Pete", "age": 27, "courses": [{"name": "a", "cost": "1.2"}]},
        {"name": "Sarah", "age": "25", "course_ids": [{"name": "b", "cost": "-11.2"}]},
    ],
}


def test__integration() -> None:
    budget, students, classrooms = load_students(**INPUT_DATA_OK)  # type: ignore

    assert budget == 125000.0
    assert students == [Student("Pete", 27, [Course("a", 1.2)]), Student("Sarah", 25, [Course("b", 11.2)])]
    assert classrooms == [
        ClassRoom("1A", 5),
        ClassRoom("1B", 3),
        ClassRoom("2A", 10),
    ]


def test__integration_errors() -> None:
    try:
        load_students(**INPUT_DATA_NOT_OK)  # type: ignore
    except ValidationErrorGroup as e:
        assert e.to_dict() == {
            "Parameter validation for load_students failed (2 sub-exceptions)": [
                {
                    "Parameter validation for Student failed (1 sub-exception)": [
                        {
                            "Parameter validation for Course failed (1 sub-exception)": [
                                {
                                    "Errors during validation of 'cost' (1 sub-exception)": [
                                        "Parameter 'cost' is invalid. Value should be greater than or equal to 0."
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "Parameter validation for ClassRoom failed (1 sub-exception)": [
                        {
                            "Errors during validation of 'name' (1 sub-exception)": [
                                "Parameter 'name' is invalid. Length too large."
                            ]
                        }
                    ]
                },
            ]
        }
