class ParsersWrapper:
    def __init__(self, parsers_names_to_use, parsers_registry, context):
        parsers_classes = list()
        for parser_name_to_use in parsers_names_to_use:
            parser_class = parsers_registry.get(parser_name_to_use)
            if parser_class is None:
                raise RuntimeError('Parser {} was not found.'.format(parser_name_to_use))
            parsers_classes.append(parser_class)
        # self._satisfy_requirements(parsers_classes)
        if not self._requirements_satisfied(parsers_classes):
            raise RuntimeError('Requirements is not satisfied')
        self.parsers = list()
        self.parsers_with_save = 0
        for parser_class in parsers_classes:
            parser = parser_class(context)
            if hasattr(parser, 'save'):
                self.parsers_with_save += 1
            self.parsers.append(parser)

    def _satisfy_requirements(self, parsers_classes):
        satisfied_requirements = list()
        for i in range(len(parsers_classes)):
            j = i + 1
            while not self._requirements_satisfied_single(parsers_classes[i], satisfied_requirements):
                if j == len(parsers_classes):
                    raise RuntimeError('Requirements can not be satisfied.')
                parsers_classes[i], parsers_classes[j] = parsers_classes[j], parsers_classes[i]
                j += 1
            satisfied_requirements.append(parsers_classes[i].__name__)

    def _requirements_satisfied_single(self, parser_class, satisfied_requirements):
        if not hasattr(parser_class, 'requirements'):
            return True
        for requirement in parser_class.requirements:
            if requirement not in satisfied_requirements:
                return False
        return True

    def _requirements_satisfied(self, parsers_classes):
        satisfied_requirements = list()
        for parser_class in parsers_classes:
            if not self._requirements_satisfied_single(parser_class, satisfied_requirements):
                return False
            satisfied_requirements.append(parser_class.__name__)
        return True

    def parse(self, context):
        for parser in self.parsers:
            parser.parse(context)

    def save(self, out_files, context, ignore=''):
        if len(out_files) != self.parsers_with_save:
            raise RuntimeError('Number of out files is not equal to number of parsers to save.')
        out_files_idx, data_parsers_idx = 0, 0
        while (out_files_idx < len(out_files)) and (data_parsers_idx < len(self.parsers)):
            if not hasattr(self.parsers[data_parsers_idx], 'save'):
                data_parsers_idx += 1
                continue
            if out_files[out_files_idx] != ignore:
                self.parsers[data_parsers_idx].save(out_files[out_files_idx], context)
            out_files_idx += 1
            data_parsers_idx += 1

    def __iter__(self):
        return iter(self.parsers)

    def __getitem__(self, key):
        return self.parsers[key]

    def __len__(self):
        return len(self.parsers)

