from functional import foldr, foldl, flip, act_foldr

# implement freeze, thaw (aren't these just constructors for IStack and MStack?)
# should inherit from Sequence and MutableSequence
# testing and docstrings needed

class Stack():
    """
    Abstract functional stack class.
    """
    # Cannot iterate over stacks longer than 993 elements.

    def __init__(self):
        """
        Empty initializer for Stacks
        """
        
        self._data = ()

    def __str__(self):
        if self:
            return "({}:{})".format(self.head, self.tail)
        else:
            return "[]"

    def __reversed__(self):
        return foldl(Stack.cons, Stack(), self)

    def __repr__(self):
        return "Stack({!r})".format(list(self))

    def __eq__(self, other):
        return type(self) is type(other) and self.raw == other.raw

    def __getitem__(self, index):
        if isinstance(index, slice):
            # how can I avoid getting the length of self?
            # getting len means I first have to traverse self.
            # note that this does not make things as effecient as they should be
            # (folds)
            return foldr(lambda i, s: s.cons(self[i]), Stack(),
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
#        if self and other:
#            # miss out on a nicer solution because adding the to last element
#            # would be really slow because of strictness
#            t1, t2 = reversed(self), other
#            for e in t1:
#                t2 = t2.cons(e)
#            return t2
#        elif self:
#            return self
#        elif other:
#            return other

    def concat(self):
        return foldr(lambda x, y: x + y, Stack(), self)

    def copy(self):
        return stackify(self.raw)

    @property
    def raw(self):
        return self._data[:]

    def cons(self, datum):
        return stackify((datum, self))

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


def stackify(s):
    """
    Makes a stack out of a raw representation.
    """
    out = Stack()
    out._data = s
    return out

class IStack(Stack):
    """
    Immutable stack.
    """
    # Cannot iterate over stacks longer than 993 elements.

    def __init__(self, data=()):
        """
        Iniitalizes stack elements in same order as data.
        """
        Stack.__init__(self)
        self._data = Stack.__add__(data, Stack()).raw

    def __repr__(self):
        return "IStack({!r})".format(list(self))

class MStack(Stack):
    """
    Mutable stack.
    """
    # Cannot iterate over stacks longer than 993 elements.

    def __init__(self, data=()):
        """
        Iniitalizes stack elements in same order as data.
        """
        Stack.__init__(self)
        act_foldr(self.push, data)

    def __repr__(self):
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
