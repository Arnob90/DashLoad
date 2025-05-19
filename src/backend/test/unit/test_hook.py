from hook import Hook


def test_hook():
    test_arr: list[str] = []

    def first_functor():
        test_arr.append("foo")

    def second_functor():
        test_arr.append("bar")

    def third_functor():
        test_arr.append("baz")

    required_hook = (
        Hook(first_functor).connect_with(second_functor).connect_with(third_functor)
    )
    required_hook()
    assert test_arr == ["foo", "bar", "baz"]
