class Stack():
    """
    Haskell style list adapted to Python.
    """
    # Cannot iterate over stacks longer than 993 elements.

    def __init__(self, data=()):
        """
        Initializes the stack in the reverse order of data.
        (This kind of makes sense since the statement "s = Stack([1,2,3])"
        sounds like "stack the elements 1 2 3" (see __reversed__))
        """
        self._data = ()
        for datum in data:
            self.cons(datum)

    def __str__(self):
        if self:
            return "{} >-{}".format(self.head(), self.tail())
        else:
            return "[]"

    def __reversed__(self):
        return Stack(self)
        # this is nice. I like this. (But maybe its bad, it seems that
        # name_of_class(instance_of_class) should == instance_of_class

    def __repr__(self):
        return "Stack({!r})".format(list(reversed(self)))

    def __eq__(self, value):
        return self.raw() == value.raw()

    def __getitem__(self, index):
        if index == 0:
            return self.head()
        else:
            return self.tail()[index - 1]

    def __setitem__(self, index, value):
        if index == 0:
            self._data[0] = value
        else:
            self.tail()[index - 1] = value

    def __delitem__(self, index):
        if index == 0:
            # for some reason self = self.tail() doesn't work
            self._data = self.tail().raw()
        else:
            del self.tail()[index - 1]

    def __len__(self):
        if self.raw():
            return 1 + len(self.tail())
        else:
            return 0

    def __iter__(self):
        if self:
            yield(self.head())
            s = iter(self.tail())
            for datum in s: # recursion alert!
                yield(datum)
        else:
            raise StopIteration
    
    def __contains__(self, value):
        return self and (self.head() == value or value in self.tail())

    def __add__(self, other):
        if self and other:
            t1, t2 = reversed(self), other
            for e in t1:
                t2.cons(e)
            return t2
        elif self:
            return self
        elif other:
            return other

    def concat(self):
        # for some reason self = self.foldr(lambda x, y: x + y, Stack()) doesn't
        # work
        self._data = self.foldr(lambda x, y: x + y, Stack()).raw()

    def concatMap(self, f):
        return reversed(Stack(map(f, self))).concat()

    def copy(self):
        s = Stack()
        s._data = self.raw()
        return s

    def raw(self):
        return self._data[:]

    def cons(self, datum):
        self._data = [datum, self.copy()] # use list for mutability

    def head(self):
        return self._data[0]

    def tail(self):
        return self._data[1]

    def take(self, n):
        if n == 0:
            return Stack()
        else:
            return self.tail().take(n - 1).cons(self.head())

    def drop(self, n):
        if n == 0:
            return self
        else:
            return self.tail().drop(n - 1)

    def init(self):
        return self.take(len(self) - 1)

    def last(self):
        if not self:
            return ()
        elif self._data[1] == ():
            return self.head()
        else:
            return self.tail().last()

    def foldl(self, f, init):
        if self:
            return self.tail().foldl(f, f(init, self.head()))
        else:
            return init

    def foldr(self, f, init):
        if self:
            return f(self.head(), self.tail().foldr(f, init))
        else:
            return init

    def foldl1(self, f):
        return self.tail().foldl(f, self.head())

    def foldr1(self, f):
        return self.tail().foldr(f, self.head())

    def spanl(self, f, init):
        ###
        ls = Stack()
        def foo(st, init):
            if self:
                ls.cons(f(init, st.head()))
                return foo(st.tail(), st.head())
            else:
                return init
        return foo(self, init)

    def spanr(self, f, init):
        pass

    def spanl1(self, f):
        pass

    def spanr1(self, f):
        pass
