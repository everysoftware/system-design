from typing import Any, Self, ClassVar

from patterns.creational.db import Database


class Multiton(type):
    """
    Multiton is a variation of the Singleton pattern where we can store multiple instances based on certain criteria.
    In our case, we can use a dictionary with a key consisting of the class name and class arguments to resolve the issue encountered in the previous section effectively.
    """

    _instances: ClassVar[dict[str, Self]] = {}

    @classmethod
    def _generate_instance_key(cls, args: Any, kwargs: Any):
        return f"{cls}:{args}:{sorted(kwargs)}"

    def __call__(cls, *args: Any, **kwargs: Any) -> Self:
        key = cls._generate_instance_key(args, kwargs)
        if key not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[key] = instance
        return cls._instances[key]


class DatabaseMultiton(Database, metaclass=Multiton):
    pass