"""Property, static, class, async methods."""


class Demo:
    @property
    def label(self) -> str:
        return "label"

    @staticmethod
    def static_run() -> str:
        return "static"

    @classmethod
    def class_run(cls) -> str:
        return "class"

    async def async_run(self) -> str:
        return "async"


def entry() -> str:
    d = Demo()
    return d.label + Demo.static_run() + Demo.class_run()
