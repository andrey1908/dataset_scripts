import os

class UniqueFilePathsGenerator:
    def __init__(self):
        self.used_file_paths = list()

    def is_used(self, file_path):
        file_path = os.path.normpath(file_path)
        for used_file_path in self.used_file_paths:
            if used_file_path == file_path:
                return True
        return False

    def is_unique(self, file_path):
        return not self.is_used(file_path)

    def add_postfix(self, file_path, postfix):
        base_name = os.path.basename(file_path)
        dir_name = os.path.dirname(file_path)
        file_path_woe, extension = os.path.splitext(base_name)
        new_file_path_woe = file_path_woe + '_{}'.format(postfix)
        new_base_name = new_file_path_woe + extension
        new_file_path = os.path.join(dir_name, new_base_name)
        return new_file_path

    def get_unique_file_path(self, file_path):
        postfix = 1
        unique_file_path = file_path
        while self.is_used(unique_file_path):
            unique_file_path = self.add_postfix(file_path, postfix)
            postfix += 1
        return unique_file_path

    def add_used_file_path(self, file_path):
        if not self.is_used(file_path):
            self.used_file_paths.append(os.path.normpath(file_path))

    def unique(self, file_path):
        unique_file_path = self.get_unique_file_path(file_path)
        self.add_used_file_path(unique_file_path)
        return unique_file_path
        
    def clear(self):
        self.used_file_paths.clear()

