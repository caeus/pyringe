import asyncio
import inspect
from dataclasses import dataclass
from types import MappingProxyType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Type,
    Union,
    cast,
)


class Getter(Protocol):
    async def __call__[T](self, type: Type[T], trace: List[type]) -> T:
        ...

    ...


class Provider[T](Protocol):
    async def __call__(
        self,
    ) -> T:
        ...


class ProviderDecorator(Protocol):
    def __call__[T](self, provider: Provider[T]) -> Provider[T]:
        ...


type Creator[T] = Callable[..., Awaitable[T]]
type Constructor[T] = Union[Type[T], Creator[T], Callable[..., T]]


@dataclass(frozen=True)
class Binding[T]:
    type: Final[Type[T]]
    using: Final[List[Type[Any]]]
    creator: Creator[T]
    decorate: ProviderDecorator

    def compile(self, getter: Getter) -> Provider[T]:
        async def provider() -> T:
            using = await asyncio.gather(*[getter(t, []) for t in self.using])
            return await self.creator(*using)

        return self.decorate(provider)


def singleton_decorator[T](provider: Provider[T]) -> Provider[T]:
    future: Optional[asyncio.Future[T]] = None

    async def decorated() -> T:
        nonlocal future
        if future is None:
            future = asyncio.Future()
            try:
                future.set_result(await provider())
            except Exception as ex:
                future.set_exception(ex)
        return await future

    return decorated
    ...


class Bind:
    __bindings: Dict[type, Binding[Any]]

    def __init__(self, bindings: Dict[type, Binding[Any]]) -> None:
        self.__bindings = bindings

    def singleton[T](self, constructor: Constructor[T]) -> None:
        signature = inspect.signature(constructor)

        if inspect.iscoroutinefunction(constructor):
            return_type = signature.return_annotation
            creator = constructor

        elif inspect.isfunction(constructor):
            return_type = signature.return_annotation

            async def creator(*args: Any) -> Any:
                return constructor(*args)
        elif inspect.isclass(constructor):
            return_type = constructor

            async def creator(*args: Any) -> Any:
                return constructor(*args)
        else:
            raise Exception("Not a class, coroutine function, or function")

        if return_type is None:
            raise Exception(
                f"Cannot bind creator function {
                    constructor} without return annotation"
            )
        self.__bindings[return_type] = Binding(
            type=return_type,
            using=[f.annotation for f in signature.parameters.values()],
            creator=creator,
            decorate=singleton_decorator,
        )
        ...


class Module(Protocol):
    def __call__(self, bind: Bind, /) -> None:
        ...


class Container:
    __bindings: MappingProxyType[type, Binding[Any]]
    __providers: Dict[type, Provider[Any]]

    def __init__(self, *modules: Module) -> None:
        bindings: Dict[type, Binding[Any]] = {}
        builder = Bind(bindings)
        for module in modules:
            module(builder)
        self.__bindings = MappingProxyType(bindings)
        self.__providers = {}

    async def _get[T: Any](self, type: Type[T], trace: List[type]) -> T:
        binding = self.__bindings.get(type)
        if binding is None:
            raise Exception(f"No binding for {type}")
        provider = self.__providers.get(type)

        if provider is None:
            provider = binding.compile(self._get)
            self.__providers[type] = provider

        return cast(type, await provider())

    async def get[T: Any](self, type: Type[T]) -> T:
        return await self._get(type, [])


def module1(bind: Bind) -> None:
    # @bind.singleton
    async def _(num: int) -> str:
        await asyncio.sleep(1)
        return str(num)

    ...


async def usage():
    container = Container(module1)
    asd = await container.get(str)
    print(asd)
