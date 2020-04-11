import os


def find_files(paths, extensions=None, known_extensions=None):
    def check_extension(file_name, extensions, known_extensions):
        if extensions is None:
            return True, None
        ext = os.path.splitext(file_name)[1]
        if ext in extensions:
            return True, None
        elif known_extensions is None:
            return False, True
        elif ext in known_extensions:
            return False, True
        else:
            return False, False

    if not isinstance(paths, (list, tuple)):
        paths = [paths]
    if isinstance(extensions, str):
        extensions = [extensions]
    if isinstance(known_extensions, str):
        known_extensions = [known_extensions]
    found_files = list()
    unknown_extensions = set()
    for path in paths:
        if os.path.isfile(path):
            target, known = check_extension(path, extensions, known_extensions)
            if target:
                found_files.append(path)
            elif not known:
                unknown_extensions.add(os.path.splitext(path)[1])
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for _file in files:
                    target, known = check_extension(_file, extensions, known_extensions)
                    if target:
                        found_files.append(os.path.join(root, _file))
                    elif not known:
                        unknown_extensions.add(os.path.splitext(_file)[1])
        else:
            raise RuntimeError('Path {} does not exist'.format(path))
    return found_files, unknown_extensions

