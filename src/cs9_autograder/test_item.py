class TestItem:
    """An item inside of the autograder"""
    __test__ = False  # tell pytest this isn't a real unit test.

    def __init__(self, correct=None, student=None, method=None, weight=None,
                 _outer_test_item=None):
        self.instance = None
        self.owner = None
        self.outer_test_item = _outer_test_item

        self._correct = correct
        self._student = student
        self._method = method
        self._weight = weight


    @property
    def correct(self):
        return self._get_var('correct')

    @property
    def student(self):
        return self._get_var('student')

    @property
    def method(self):
        return self._get_var('method')

    @property
    def weight(self):
        return self._get_var('weight')

    def _get_var(self, var_name):
        search_objs = [(self, f'_{var_name}'),
                       (self.instance, var_name),
                       (self.owner, var_name),
                       (self.outer_test_item, var_name)]
        for obj, name in search_objs:
            try:
                if var := getattr(obj, name):
                    return var
            except AttributeError:
                pass

        raise AttributeError(f'Cannot find attribute {var_name}. '
                             f'self.instance is {self.instance}; '
                             f'self.owner is {self.owner}.')

    def __set_name__(self, owner, name):
        self.owner = owner

    def __get__(self, instance, owner=None):
        """Should be called from the __get__ method."""
        self.instance = instance
        if owner:
            self.owner = owner
