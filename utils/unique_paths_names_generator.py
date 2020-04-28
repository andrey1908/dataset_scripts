import os


class UniquePathsNamesGenerator:
    def __init__(self):
        self.used_paths_names = set()
        self.postfix = 1

    def is_used(self, path_name):
        path_name = os.path.normpath(path_name)
        return path_name in self.used_paths_names

    def is_unique(self, path_name):
        return not self.is_used(path_name)

    def _add_postfix(self, path_name, postfix):
        path_name_woe, extension = os.path.splitext(path_name)
        new_path_name_woe = os.path.normpath(path_name_woe) + postfix
        new_path_name = new_path_name_woe + extension
        return new_path_name

    def get_unique_path_name(self, path_name):
        new_path_name = path_name
        while self.is_used(new_path_name):
            new_path_name = self._add_postfix(path_name, '_{}'.format(self.postfix))
            self.postfix += 1
        return new_path_name

    def add_used_path_name(self, path_name):
        if not self.is_used(path_name):
            self.used_paths_names.add(os.path.normpath(path_name))

    def unique(self, path_name):
        unique_path_name = self.get_unique_path_name(path_name)
        self.used_paths_names.add(os.path.normpath(unique_path_name))
        return unique_path_name
        
    def clear(self):
        self.used_paths_names.clear()
        self.postfix = 1

