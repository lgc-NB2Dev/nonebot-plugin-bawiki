from typing import Literal, overload

from nonebot.compat import PYDANTIC_V2

__all__ = ("field_validator", "model_validator")

if PYDANTIC_V2:
    from pydantic import (
        field_validator as field_validator,  # type: ignore
        model_validator as model_validator,
    )
else:
    from pydantic import root_validator, validator

    @overload
    def model_validator(*, mode: Literal["before"]):
        ...

    @overload
    def model_validator(*, mode: Literal["after"]):
        ...

    def model_validator(*, mode: Literal["before", "after"]):
        return root_validator(pre=mode == "before", allow_reuse=True)  # type: ignore

    def field_validator(
        __field: str,
        *fields,
        mode: Literal["before", "after"] = "after",
    ):
        return validator(__field, *fields, pre=mode == "before", allow_reuse=True)
