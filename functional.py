from collections.abc import Mapping

# Can I make an natcheck or intcheck function so I can avoid rewriting it all
# the time? (But I don't wan't to export it)
# maybe I can implement folds using iter?

def to_args(f):
    """
    function -> function

    Converts a function that takes one collection of arguments to a function
    that takes multiple arguments.

    >>> to_args(sum)(1,2,3,4)
    10
    >>> to_args(lambda d: d["a"])(a=1)
    1
    """
    return lambda *args, **kwargs: f(*filter(bool, (args, kwargs)))

def to_argcollection(f):
    """
    function -> function

    Converts a function that takes multiple arguments to a function that takes
    one collection of arguments. The new function can take either a Mapping or
    an Iterable.

    >>> add4 = lambda a, b, c, d: a + b + c + d
    >>> to_argcollection(add4)([1, 2, 3 ,4])
    10
    >>> to_argcollection(add4)({"a": 1, "b": 2, "c": 3, "d": 4})
    10
    """
    return lambda args: f(**args) if isinstance(args, Mapping) else f(*args)

def flip(f):
    """
    function -> function

    Flips the order of the first two arguments of a function.

    >>> list(flip(zip)([1,2],[3,4]))
    [(3, 1), (4, 2)]
    """
    return lambda x, y: f(y, x)

def const(x, *y, **z):
    """
    (a, ...) -> a

    Returns the first input and ignores the rest. This means that it also acts
    as the identity function when given only one input.

    >>> const(1, 2)
    1
    >>> const(1)
    1
    >>> const(1, 2, 3, 4, 5)
    1
    """
    return x

# Is there a better name for this?
def stretch(f, n=1):
    """
    (function, natural number) -> function

    Returns a function that equals f except that it requires n extra arguments
    in the front.

    >>> stretch(to_args(sum), 2)(10, 20, 1, 2, 3)
    6
    """
    if 0 <= n == int(n):
        return curry(curry(const)(stretch(f, n - 1)), -1) if n else f
    else:
        raise ValueError("n must be a natural number.")

def apply(f, *args, **kwargs):
    """
    (a -> b, a) -> b

    Returns applies the function to the argument(s).

    >>> apply(lambda x: x + 1, 5)
    6
    >>> functions = [lambda x: x + 1, lambda x: 2 * x, lambda x: x ** 2]
    >>> list(map(curry(flip(apply))(3), functions))
    [4, 6, 9]
    >>> list(zip_with(apply, functions, [5, 4, 3]))
    [6, 8, 9]
    """
    return f(*args, **kwargs)

def curry(f, n=1):
    """
    (function, natural number) -> function

    Generalized currying and uncurrying.

    If f is composed of k partial functions, then curry(f,n) is composed of k +
    n partial functions, with arguments distributed among the functions
    arbitrarily.

    Note that only once-uncurried functions can take a keyword argument for the
    first paramater, and the name of that argument is 'x'.

    >>> add4 = lambda a, b, c, d: a + b + c + d
    >>> add4(1, 2, 3, 4)
    10
    >>> curry(add4)(1, 2)(3, 4)
    10
    >>> curry(add4, 2)(1)(2, 3)(4)
    10
    >>> curry(curry(add4, 3), -1)(1)(2)(3, 4) # this is like curry(add4, 2)
    10
    >>> curry(curry(const)(add4), -1)(10, 1, 1, 1, 1) # this is stretch(add4)
    4
    >>> curry(add4)(d=4, c=3)(1, 2)
    10
    >>> curry(curry(add4, 3), -1)(x=1)(d=2)(3, c=4)
    10
    """
    if n != int(n): # the type does not need to be an integer, the value does
        raise ValueError("n must be an integer.")
    if n > 0:
        return lambda *x, **y: curry(lambda *args, **kwargs: f(*(x + args),
                                                               **dict(y,
                                                               **kwargs)),
                                     n - 1)
    elif n < 0:
        # Do I really want the kwargs for this?
        # (If not, remember to change docstring)
        # That the only name it can take is 'x' makes it very yucky.
        # (There's no way to extract the original name, is there?)
        return lambda x, *args, **kwargs: curry(f(x), n + 1)(*args, **kwargs)
    else:
        return f

def foldr(f, acc, xs):
    """
    ((a, b) -> b, b, collection of a) -> b

    Right-associative fold.

    Applies the binary operator (f) on the elements of the collection (xs)
    right-associatively, that is, with the innermost operation at the end, and
    the outermost operation at the beginning. The innermost operation uses the
    accumulator (acc).

    >>> foldr(lambda x, y: x ** y, 2, [2, 2, 2])
    65536
    """
    return f(xs[0], foldr(f, acc, xs[1:])) if xs else acc

def foldl(f, acc, xs):
    """
    ((b, a) -> b, b, collection of a) -> b

    Left-associative fold.

    Applies the binary operator (f) on the elements of the collection (xs)
    left-associatively, that is, with the innermost operation at the beginning,
    and the outermost operation at the end. The innermost operation uses the
    accumulator (acc).

    >>> foldl(lambda x, y: x ** y, 2, [2, 2, 2])
    256
    """
    return foldl(f, f(acc, xs[0]), xs[1:]) if xs else acc

def foldr1(f, xs):
    """
    ((a, b) -> b, collection of a) -> b

    Right-associative fold on non-empty collections.

    Applies the binary operator (f) on the elements of the collection (xs)
    right-associatively, that is, with the innermost operation at the end, and
    the outermost operation at the beginning.

    >>> foldr1(lambda x, y: x ** y, [2, 2, 2, 2])
    65536
    """
    return foldr(f, xs[0], xs[1:])

def foldl1(f, xs):
    """
    ((b, a) -> b, collection of a) -> b

    Left-associative fold on non-empty collections.

    Applies the binary operator (f) on the elements of the collection (xs)
    left-associatively, that is, with the innermost operation at the beginning,
    and the outermost operation at the end.

    >>> foldl1(lambda x, y: x ** y, [2, 2, 2, 2])
    256
    """
    return foldl(f, xs[0], xs[1:])

def scanr(f, acc, xs):
    """
    ((a, b) -> b, b, collection of a) -> list of b

    foldr and collect intermediate results.

    >>> scanr(to_args(sum), 0, [1, 2, 3, 4, 5])
    [15, 14, 12, 9, 5, 0]
    """
    if xs:
        ys = scanr(f, acc, xs[1:])
        return [f(xs[0], ys[0])] + ys
    else:
        return [acc]

def scanl(f, acc, xs):
    """
    ((b, a) -> b, b, collection of a) -> list of b

    foldl and collect intermediate results.

    >>> scanl(to_args(sum), 0, [1, 2, 3, 4, 5])
    [0, 1, 3, 6, 10, 15]
    """
    return [acc] + (scanl(f, f(acc, xs[0]), xs[1:]) if xs else [])

def scanr1(f, xs):
    """
    ((a, b) -> b, collection of a) -> list of b

    foldr1 and collect intermediate results.

    >>> scanr1(to_args(sum), [1, 2, 3, 4, 5])
    [15, 14, 12, 9, 5]
    """
    # depending on the data struct, it might be more efficient to reimplement
    # the algorithm and just check for a singleton instead of empty
    # (eg Haskell lists)
    return scanr(f, xs[-1], xs[:-1])

def scanl1(f, xs):
    """
    ((b, a) -> b, collection of a) -> list of b

    foldl1 and collect intermediate results.

    >>> scanl1(to_args(sum), [1, 2, 3, 4, 5])
    [1, 3, 6, 10, 15]
    """
    return scanl(f, xs[0], xs[1:])

def act_foldr(f, xs):
    """
    (a -> NoneType, collection of a) -> NoneType

    Sequence actions over xs right-associatively.

    >>> l = [5, 4, 3]
    >>> act_foldr(l.append, [1, 2])
    >>> l
    [5, 4, 3, 2, 1]
    """
    foldr(flip(stretch(f)), None, xs)

def act_foldl(f, xs):
    """
    (a -> NoneTypem, collection of a) -> NoneType

    Sequence actions over xs left-associatively.

    >>> l = [1, 2, 3]
    >>> act_foldl(l.append, [4, 5])
    >>> l
    [1, 2, 3, 4, 5]
    """
    foldl(stretch(f), None, xs)

def comp(*fs):
    """
    (unary functions) -> unary function

    Polyvariadic function composition.

    The output function passes the intermediate results of the input functions
    from right to left.

    >>> succ = lambda x: x + 1
    >>> pred = lambda x: x - 1
    >>> comp(succ,pred)(1)
    1
    >>> comp(succ,succ,comp(pred,succ,pred))(1)
    2
    """
    return foldr(lambda f, g: lambda x: f(g(x)), const, fs)

def zip_with(f, *xs):
    """
    (function, iterables) -> map

    Zips the iterables and then uses the elements of each resulting collection
    as the arguments for the function.

    >>> list(zip_with(to_args(sum), (1, 2), (3, 4)))
    [4, 6]
    """
    return map(to_argcollection(f), zip(*xs))

def join_iters(*iters):
    """
    iterations -> iteration

    Joins iterations one after another.

    >>> a, b = enumerate([1, 2]), enumerate([3,4])
    >>> for i in join_iters(a, b): print(i)
    (0, 1)
    (1, 2)
    (0, 3)
    (1, 4)
    """
    for it in iters:
        for e in it:
            yield(e)
    # this should raise StopIteration automatically

#testing
# this should be better since it doesn't use indexing, and more importantly, it
# doesn't use slices
def ifoldr(f, acc, xs):
    def go(it):
        try:
            return f(next(it), go(it))
        except StopIteration:
            return acc
    return go(iter(xs))

def ifoldl(f, acc, xs):
    def go(ac, it):
        try:
            return go(f(ac, next(it)), it)
        except StopIteration:
            return ac
    return go(acc, iter(xs))

# this version should return an iterator (laziness, yay!)
def iscanr(f, acc, xs):
    def go(it):
        try:
            x = next(it)
            its = go(it)
            y = next(its)
            return join_iters(iter([f(x, y)]), iter([y]), its)
        except StopIteration:
            return iter([acc])
    return go(iter(xs))

def iscanl(f, acc, xs):
    def go(ac, it):
        try:
            # this relies on 'next(it)' appearing before 'it'
            return join_iters(iter([ac]), go(f(ac, next(it)), it))
        except StopIteration:
            return iter([ac])
    return go(acc, iter(xs))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
