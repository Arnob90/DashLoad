from typing import Callable


class Hook:
    def __init__(self, given_functor: Callable[[], None] = lambda: None) -> None:
        self.functor = given_functor

    def connect_with(self, functor_to_compose_with: Callable[[], None]):
        # Copy the function pointer so it does not change
        previous_functor = self.functor

        def connected_functor():
            previous_functor()
            functor_to_compose_with()

        self.functor = connected_functor
        return self

    def __call__(self) -> None:
        self.functor()
