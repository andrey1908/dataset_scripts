class Registry:
    def __init__(self):
        self.classes = dict()

    def register(self, cls):
        self.classes[cls.__name__] = cls
        return cls

    def get(self, cls_name):
        return self.classes.get(cls_name)

