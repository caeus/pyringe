import asyncio
from dataclasses import dataclass
from typing import Annotated, Protocol

from pyringe.container import Bind, Container


class Color(Protocol):
    def __call__(self) -> str:
        ...


class Shape(Protocol):
    def __call__(self) -> str:
        ...


@dataclass(frozen=True)
class Drawing:
    color: Color
    shape: Shape

    @property
    def description(self) -> str:
        return f"A {self.shape()} of {self.color()} color"


async def _test_container():
    def module1(bind: Bind) -> None:
        @bind.singleton
        async def _() -> Color:
            def color() -> str:
                return "RED"

            await asyncio.sleep(3)
            return color

        @bind.singleton
        def _() -> Shape:
            def shape() -> Annotated[str, "sdf"]:
                return "SQUARE"

            return shape

        bind.singleton(Drawing)

        @bind.singleton
        def _() -> Shape:
            def shape() -> Annotated[str, "sdf"]:
                return "CIRCLE"

            return shape

    container = Container(module1)
    assert (await container.get(Drawing)).description == "A CIRCLE of RED color"


def test_container():
    asyncio.run(_test_container())
