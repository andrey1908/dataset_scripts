import os
from dataset_scripts.utils import Context
from .registry import WAYMO_PARSERS_REGISTRY


@WAYMO_PARSERS_REGISTRY.register
class EnvironmentParser:
    requirements = ('ImagesParser',)

    def __init__(self, context):
        self.images_files = list()
        self.time_of_day = list()
        self.location = list()
        self.weather = list()

    def parse(self, context):
        root_folder = context.root_folder if context.valid_attr('root_folder') else context.out_images_folder
        self.images_files.append(os.path.relpath(context.ImagesParser_context.image_file, root_folder))
        self.time_of_day.append(str(context.frame.context.stats.time_of_day))
        self.location.append(str(context.frame.context.stats.location))
        self.weather.append(str(context.frame.context.stats.weather))

    def save(self, out_file, context):
        lines = list()
        for image_file, time_of_day, location, weather in zip(self.images_files, self.time_of_day, self.location, self.weather):
            if time_of_day == '':
                time_of_day = '-'
            if location == '':
                location = '-'
            if weather == '':
                weather = '-'
            line = ' '.join([image_file, time_of_day, location, weather]) + '\n'
            lines.append(line)
        with open(out_file, 'w') as f:
            f.writelines(lines)

