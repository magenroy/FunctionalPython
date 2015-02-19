from functional import foldr, foldl, flip, act_foldr
from collections import Sequence, MutableSequence

# should inherit from Sequence and MutableSequence
# testing and docstrings needed
# should there be a data argument in the abstract Stack initializer?
# should I even make a __repr__ for abstract Stack?
# its hard to use Stack instances in docstrings for Stack

# don't forget to implement the appropriate methods for Sequence
class Stack(Sequence):
    """
    Abstract functional stack class.
    """
    # Cannot iterate over stacks longer than 993 elements.

    def __init__(self, data=()):
        """
        Stack -> NoneType

        Iniitalizes stack elements in same order as data.

        >>> Stack(range(4))
        Stack([0, 1, 2, 3])
        >>> Stack()
        Stack([])
        """
        
        self._data = ()
        self._data = Stack.__add__(data, type(self)()).raw if data else self._data

    def __str__(self):
        """
        Stack -> str

        Human readable string representation of a Stack based on Haskell
        implementation of lists.

        >>> str(Stack([1,2]))
        '(1:(2:[]))'
        """
        return "({}:{})".format(self.head, self.tail) if self else "[]"

    def __reversed__(self):
        """
        Stack -> Stack

        Returns a new Stack with the order of the elements reversed.
        >>> reversed(stackify((1,stackify((2, Stack())))))
        Stack([2, 1])
        """
        return foldl(Stack.cons, type(self)(), self)

    def __repr__(self):
        """
        Stack -> str

        Evaluatable string representation of IStack.

        >>> s = Stack([1, 2, 3])
        >>> s == eval(repr(s))
        True
        >>> repr(s)
        'Stack([1, 2, 3])'
        >>>
        """
        # glory to abstractions!
        return "{}({!r})".format(type(self).__name__, list(self))

    def __eq__(self, other):
        """
        (Stack, Stack) -> bool

        Checks for equality of Stacks.

        >>> Stack() == Stack()
        True
        >>> Stack([1, 2, 3]) == Stack((1, 2, 3))
        True
        """
        return type(self) is type(other) and self.raw == other.raw

    # UNFINISHED!!!
    def __getitem__(self, index):
        """
        (Stack, natural number or slice) -> Stack

        Stack.__getitem__(s, i) <==> s[i]

        >>> s = Stack(range(10))
        >>> s[3]
        3
        >>> s[-2] 
        8
        >>> s[2:7:2]
        Stack([2, 4, 6])
        >>> s[5:]
        Stack([5, 6, 7, 8, 9])
        >>> s[4::2]
        Stack([4, 6, 8])
        >>> s[:3]
        Stack([0, 1, 2])
        >>> s[:7:2]
        Stack([0, 2, 4, 6])
        >>> s[6::-2]
        Stack([6, 4, 2, 0])
        >>> s[6:3:-2]
        Stack([6, 4])
        """
        if isinstance(index, slice):
            # can this be cleaner?
            step = 1 if index.step is None else index.step
            if index.start is None and index.stop is None:
                # I could use filter and mod, but I don't know how filter will
                # behave
                return foldr(lambda ie, s: s.cons(ie[1]) if ie[0] % step == 0
                        else s, type(self)(), enumerate(self))
            else:
                # I first chop off the ends so that I don't need to perform a
                # check when I traverse them (infinitesimal optimization,
                # consider removing for the sake of prettiness, on the other
                # hand, the predicate in the other case will become uglier if I
                # remove this...)
                start = 0 if index.start is None else index.start
                s = self.drop(start)
                return (s if index.stop is None else
                        s.take(index.stop))[::index.step]
                #return self.drop(start).take(index.stop - start)[::index.step]
        else:
            # actually, I should be correctly handling negative indices...
            # use modulo
            if 0 <= index == int(index):
                go = lambda s, i: go(s.tail, i - 1) if i else s.head
                return go(self, index)
            else:
                raise ValueError("index must be a natural number.")

    def __len__(self):
        """
        Stack -> int

        Returns the number of elements in the Stack.

        >>> len(Stack())
        0
        >>> len(Stack(range(100)))
        100
        """
        return 1 + len(self.tail) if self.raw else 0

    def __iter__(self):
        """
        Stack -> iteration

        Returns an iteration of the Stack.

        >>> s = Stack(range(3))
        >>> for e in s: print(e, end=" ")
        0 1 2 
        """
        if self:
            yield(self.head)
            s = iter(self.tail)
            for datum in s: # recursion alert!
                yield(datum)
        else:
            raise StopIteration
    
    def __contains__(self, value):
        """
        (Stack of a, a) -> bool

        Checks for if the value is in the Stack.

        >>> 1 in Stack()
        False
        >>> 2 in Stack([1, 2, 3])
        True
        """
        return self and (self.head == value or value in self.tail)

    def __add__(self, other):
        return foldr(flip(Stack.cons), other, self)

    def concat(self):
        return foldr(lambda x, y: x + y, type(self)(), self)

    def copy(self):
        return stackify(self.raw)

    @property
    def raw(self):
        return self._data

    def cons(self, datum):
        return stackify((datum, self), type(self))

    @property
    def head(self):
        return self._data[0]

    @property
    def tail(self):
        return self._data[1]

    def take(self, n):
        if 0 <= n == int(n):
            go = lambda s, i: go(s.tail, i - 1).cons(s.head) if i else type(self)()
            return go(self, n)
        else:
            raise ValueError("n must be a natural number.")

    # it seems like this should replace tail and just have n=1 default, but then
    # I can't make it a property
    def drop(self, n):
        if 0 <= n == int(n):
            go = lambda s, i: go(s.tail, i - 1) if i else s
            return go(self, n)
        else:
            raise ValueError("n must be a natural number.")

    @property
    def init(self):
        return self.take(len(self) - 1)

    @property
    def last(self):
        return self[-1]


def stackify(s, t=Stack):
    """
    Makes a stack out of a raw representation.
    """
    out = t()
    out._data = s
    return out

class IStack(Stack):
    """
    Immutable stack.
    """
    # Cannot iterate over stacks longer than 993 elements.

    def __init__(self, data=()):
        """
        (IStack, iterable) -> NoneType

        Iniitalizes stack elements in same order as data.

        >>> IStack(range(4))
        IStack([0, 1, 2, 3])
        """
        Stack.__init__(self, data)

    def __repr__(self):
        """
        IStack -> str

        Evaluatable string representation of IStack.

        >>> s = IStack([1, 2, 3])
        >>> s == eval(repr(s))
        True
        >>> repr(s)
        'IStack([1, 2, 3])'
        """

        return "IStack({!r})".format(list(self))


class MStack(Stack):
    """
    Mutable stack.
    """
    # Cannot iterate over stacks longer than 993 elements.

    def __init__(self, data=()):
        """
        (MStack, iterable) -> NoneType

        Iniitalizes stack elements in same order as data.

        >>> MStack(range(4))
        MStack([0, 1, 2, 3])
        """
        Stack.__init__(self)
        act_foldr(self.push, data)

    def __repr__(self):
        """
        MStack -> str

        Evaluatable string representation of MStack.

        >>> s = MStack([1, 2, 3])
        >>> s == eval(repr(s))
        True
        >>> repr(s)
        'MStack([1, 2, 3])'
        """
        return "MStack({!r})".format(list(self))

    def __setitem__(self, index, value):
        if 0 <= index == int(index):
            def go(s, i):
                if i:
                    go(s.tail, i - 1)
                else:
                    s._data[0] = value
            go(self, index)
        else:
            raise ValueError("index must be a natural number.")

    def __delitem__(self, index):
        if 0 <= index == int(index):
            def go(s, i):
                if i:
                    go(s.tail, i - 1)
                else:
                    s._data = s.tail.raw
            go(self, index)
        else:
            raise ValueError("index must be a natural number.")

    def concat(self):
        self._data = foldr(lambda x, y: x + y, MStack(), self).raw

    def push(self, datum):
        self._data = [datum, self.copy()] # use list for mutability

    def pop(self):
        out = self._data[0]
        self._data = self.tail.raw
        return out

if __name__ == "__main__":
    import doctest
    doctest.testmod()
