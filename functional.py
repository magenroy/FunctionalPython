def to_args(f):
    """
    function -> function

    Converts a function that takes one collection of arguments to a function
    that takes multiple arguments.

    >>> to_args(sum)(1,2,3,4)
    10
    """
    return lambda *args: f(args)

def to_arglist(f):
    """
    function -> function

    Converts a function that takes multiple arguments to a function that takes
    one collection of arguments.
    >>> to_arglist(lambda a, b, c, d: a + b + c + d)([1, 2, 3 ,4])
    10
    """
    return lambda args: f(*args)

def flip(f):
    return lambda x, y: f(y, x)

def curry(f, n=1):
    """
    (function, int) -> function

    Generalized currying and uncurrying.

    If f is composed of k partial functions, then curry(f,n) is composed of k +
    n partial functions, with arguments distributed among the functions
    arbitrarily.

    >>> add4 = lambda a, b, c, d: a + b + c + d
    >>> add4(1, 2, 3, 4)
    10
    >>> curry(add4)(1, 2)(3,4)
    10
    >>> curry(add4, 2)(1)(2, 3)(4)
    10
    >>> curry(curry(add4, 3), -1)(1)(2)(3, 4) # this is like curry(add4, 2)
    10
    """
    if n != int(n): # the type does not need to be an integer, the value does
        raise ValueError("n must be an integer.")
    if n > 0:
        return lambda *x: curry(lambda *args: f(*(x + args)), n - 1)
    elif n < 0:
        return lambda x, *args: curry(f(x), n + 1)(*args)
    else:
        return f

def foldr(f, acc, xs):
    """
    ((a, b) -> b, b, collection of a) -> b

    Right-associative fold.

    Applies the binary operator on the elements of the collection with the
    innermost operation at the end, and the outermost operation at the
    beginning.

    >>> foldr(lambda x, y: x ** y, 2, [2, 2, 2])
    65536
    """
    return f(xs[0], foldr(f, acc, xs[1:])) if xs else acc

def foldl(f, acc, xs):
    """
    ((b, a) -> b, b, collection of a) -> b

    Left-associative fold.

    Applies the binary operator on the elements of the collection with the
    innermost operation at the beginning, and the outermost operation at the
    end.

    >>> foldl(lambda x, y: x ** y, 2, [2, 2, 2])
    256
    """
    return foldl(f, f(acc, xs[0]), xs[1:]) if xs else acc

def foldr1(f, xs):
    """
    ((a, b) -> b, collection of a) -> b

    Right-associative fold on non-empty collections.

    Applies the binary operator on the elements of the collection with the
    innermost operation at the end, and the outermost operation at the
    beginning.

    >>> foldr1(lambda x, y: x ** y, [2, 2, 2, 2])
    65536
    """
    return foldr(f, xs[0], xs[1:])

def foldl1(f, xs):
    """
    ((b, a) -> b, collection of a) -> b

    Left-associative fold on non-empty collections.

    Applies the binary operator on the elements of the collection with the
    innermost operation at the beginning, and the outermost operation at the
    end.

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

def comp(*fs):
    """
    (function, function) -> function

    Somewhat generalized function composition.

    The new function takes as many arguments as the last function given. It
    passes the results from right to left.

    >>> succ = lambda x: x + 1
    >>> pred = lambda x: x - 1
    >>> comp(succ,pred)(1)
    1
    >>> comp(succ,succ,comp(pred,succ,pred))(1)
    2
    """
    return foldr(lambda f, g: lambda x: f(g(x)), lambda x: x, fs)

def zip_with(f, *xs):
    """
    (function, iterables) -> map

    Zips the iterables and then uses the elements of each resulting collection
    as the arguments for the function.

    >>> list(zip_with(to_args(sum), (1, 2), (3, 4)))
    [4, 6]
    """
    return map(to_arglist(f), zip(*xs))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
