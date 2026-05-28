"""Mirrors FeatureDrafter(llm).domain_method() pattern."""


class DomainClass:
    def domain_method(self, arg: str) -> str:
        return self._helper() + arg

    def _helper(self) -> str:
        return "domain-"


def entry(dep: str, story: str) -> str:
    return DomainClass(dep).domain_method(story)
