class Context:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def update(self, **kwargs):
        self.__dict__.update(kwargs)

    def valid_attr(self, attr):
        return self.__dict__.get(attr) is not None

