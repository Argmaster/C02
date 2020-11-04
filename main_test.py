import overload

@overload.Overload
def func(a: str, b: int):
    print(a, b)

@overload.Overload
def func(a: float, b: float):
    print(a, b)

func(1.0, 1.0)