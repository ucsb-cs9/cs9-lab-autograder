def differential(correct_items, student_items, assertion=None,
                 normalize=None, msg=None):
    """A decorator to which converts a function into a differential test.

    The decorated function is called twice. First with correct_items, then
    with student_items.
    The returned values of the decorated function are then compared to
    determine if the student's implementation is correct.

    assertion: The method to call instead of assertEqual
    normalize: A function which normalizes the two returned values before
        comparison.
    msg: The msg to be passed to the assertion method.
    """

    def decorator(wrapped_method):
        def wrapper(self):
            expected = wrapped_method(self, correct_items)
            actual = wrapped_method(self, student_items)

            if normalize:
                expected = normalize(expected)
                actual = normalize(actual)

            if assertion:
                assertion(self, expected, actual, msg=msg)

            else:
                self.assertEqual(expected, actual, msg=msg)

        return wrapper
    return decorator
