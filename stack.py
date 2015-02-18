from functional import foldr, foldl, flip, act_foldr

# Fix the problem with instances not being from correct classes
#   I think I have done this by using type(self) to get the constructor in the
#   right places
# implement freeze, thaw (aren't these just constructors for IStack and MStack?)
# should inherit from Sequence and MutableSequence
# testing and docstrings needed
# should there be a data argument in the abstract Stack initializer?
# should I even make a __repr__ for abstract Stack?
# its hard to use Stack instances in docstrings for Stack
# maybe should

class Stack():
    """
    Abstract functional stack class.
    """
    # Cannot iterate over stacks longer than 993 elements.

    def __init__(self):
        """
        Stack -> NoneType

        Empty initializer for Stacks.

        >>> Stack()
        Stack([])
        """
        
        self._data = ()

    def __str__(self):
        """
        Stack -> str

        Human readable string representation of a Stack based on Haskell
        implementation of lists.

        >>> str(stackify((1,stackify((1, Stack())))))
        '(1:(1:[]))'
        """
        return "({}:{})".format(self.head, self.tail) if self else "[]"

    def __reversed__(self):
        """
        Stack -> Stack

        Returns a new Stack with the order of the elements reversed.
        >>> reversed(stackify((1,stackify((2, Stack())))))
        Stack([2, 1])
        """
        return foldl(Stack.cons, Stack(), self)

    def __repr__(self):
        """
        Stack -> str

        Not valid for abstract Stacks.
        """
        return "Stack({!r})".format(list(self))

    def __eq__(self, other):
        """
        (Stack, Stack) -> bool

        Checks for equality of Stacks.

        >>> Stack() == Stack()
        True
        """
        return type(self) is type(other) and self.raw == other.raw

    def __getitem__(self, index):
        """
        (Stack, natural number or slice) -> Stack

        Stack.__getitem__(s, i) <==> s[i]

        >>> s = IStack(range(10))
        >>> s[3]
        3
        >>> s[2:7:2]
        IStack([2, 4, 6])
        """
        if isinstance(index, slice):
            # how can I avoid getting the length of self?
            # getting len means I first have to traverse self.
            # note that this implementation does is not as effecient as it
            # should be even without getting len (eg folds)
            # using enums and the iter based folds, I should be able to makes
            # this run in linear time.
            return foldr(lambda i, s: s.cons(self[i]), type(self)(),
                         range(*index.indices(len(self))))
        else:
            if 0 <= index == int(index):
                go = lambda s, i: go(s.tail, i - 1) if i else s.head
                return go(self, index)
            else:
                raise ValueError("index must be a natural number.")

    def __len__(self):
        return 1 + len(self.tail) if self.raw else 0

    def __iter__(self):
        if self:
            yield(self.head)
            s = iter(self.tail)
            for datum in s: # recursion alert!
                yield(datum)
        else:
            raise StopIteration
    
    def __contains__(self, value):
        return self and (self.head == value or value in self.tail)

    def __add__(self, other):
        return foldr(flip(Stack.cons), other, self)

    def concat(self):
        return foldr(lambda x, y: x + y, Stack(), self)

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
            go = lambda s, i: go(s.tail, i - 1).cons(s.head) if i else Stack()
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
        Stack.__init__(self)
        self._data = Stack.__add__(data, Stack()).raw

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
