"""
Base class for any traits to define.
"""
import abc
import inspect

from nekosquared.shared import alg


class BaseTraitMeta(type, abc.ABCMeta):
    """
    Metaclass for traits. This just overloads some of the builtin methods
    and defines empty slots.
    """
    __slots__ = ()

    @property
    def cls_name(cls):
        return cls.__name__

    def __str__(cls):
        return f'{cls.cls_name} class defn'

    def __repr__(cls):
        mcs = __class__
        # noinspection PyBroadException
        try:
            file = inspect.getfile(cls)
        except TypeError:
            file = None
        finally:
            if not file:
                file = 'UNKNOWN'

        return f'<{cls.cls_name} defn mcs={mcs.__name__!r} file={file!r}>'


class BaseTrait(metaclass=BaseTraitMeta):
    """
    Base class for traits to implement. This does not implement ``__slots__``
    as cached properties require that a class have a dict implementation
    underneath. Usage of ``__slots__`` prevents these property caches from
    functioning correctly.

    This also implements a custom "magic method" called ``__init_class__``.
    This is a method that can be defined when a derived class is declared, and
    works in a similar way to ``__init__``, except it will only operate on
    the class once, and gets called when the class is initialised at runtime,
    just as ``__init_subclass__`` is.

    NOTE: you must NOT call ``super`` in this magic method to invoke a parent
    implementation.
    """
    __slots__ = ('__base_traits__',)

    def __init_subclass__(cls, **kwargs):
        """
        Initialise the subclass. If there is an ``__init_class__`` member, then
        call it.
        :param kwargs: keyword arguments.
        """
        init = alg.find(lambda m: getattr(m, '__name__') == '__init_class__',
                        inspect.getmembers(cls, inspect.ismethod))

        if init:
            init(**kwargs)

        # Get the base traits
        cls.__base_traits__ = {
            alg.find_all(
                lambda c: issubclass(c, __class__),
                cls.mro()
            )
        }

    @property
    def cls_name(self):
        return type(self).cls_name

    def __str__(self):
        return f'{self.cls_name} class inst'

    def __repr__(self):
        # noinspection PyBroadException
        try:
            file = inspect.getfile(type(self))
        except TypeError:
            file = None
        finally:
            if not file:
                file = 'UNKNOWN'

        return (
            f'<{self.cls_name} inst bases={" ".join(self.__base_traits__)!r} '
            f'mcs={type(type(self))!r} file={file!r}>'
        )
