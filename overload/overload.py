from inspect import signature as sig

Any = object


class NoMatchingOverload(Exception):
    pass


class OverloadedObject:
    """Object representing overloaded function"""

    def __init__(self, func_name: str) -> None:
        """Instance contains only reference to Overload singletone
        and function name

        Args:
            func_name (str): name of function represented
        """
        self._name = func_name

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return Overload.call(self, args, kwargs)


class Overload:

    __func__ = {}
    __instance__ = None

    def __new__(cls, func: callable) -> OverloadedObject:
        # create singleton instance if no exists
        if cls.__instance__ is None:
            cls.__instance__ = object.__new__(cls)
        # return created OverloadedObject
        return cls.__instance__.__overload__(func)

    @classmethod
    def __overload__(cls, func: callable) -> OverloadedObject:
        if func.__qualname__ in cls.__func__.keys():
            cls.__func__[func.__qualname__].add(func)
        else:
            cls.__func__[func.__qualname__] = {func}
        return OverloadedObject(func.__qualname__)

    @classmethod
    def call(cls, overObj, args, kwargs) -> Any:
        # get count of keyword args
        c_kwarg_count = len(kwargs)
        # get count of all args
        c_arg_count = len(args) + c_kwarg_count
        # for each overload execute following tests
        for func in cls.__func__[overObj._name]:
            try:
                # try binding arguments (test if args match)
                sig(func).bind(*args, **kwargs)
                f_parm = sig(func).parameters
                for index, key in enumerate(f_parm.keys()):
                    hint = f_parm[key].annotation
                    empty = f_parm[key].empty
                    if index < len(args):
                        if not (isinstance(args[index], hint) or hint == empty):
                            raise TypeError()
                    else:
                        if not (isinstance(kwargs[key], hint) or hint == empty):
                            raise TypeError()
                # call function if no exception is raised
                return func(*args, **kwargs)
            except TypeError:
                pass
        else:
            raise NoMatchingOverload(
                f"No matching overload for arguments: {args} {kwargs}"
            )
