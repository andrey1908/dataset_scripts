import os
from dataset_scripts.utils import Context
from .registry import WAYMO_PARSERS_REGISTRY


@WAYMO_PARSERS_REGISTRY.register
class TestFrameContextName:
    def __init__(self, context):
        self.context_name = None
        self.tfrecord_file = None
        self.out_lines = list()
        
    def parse(self, context):
        if self.tfrecord_file == context.tfrecord_file:
            if self.context_name != context.frame.context.name:
                self.out_lines.append('File {} has different frame context names\n'.format(self.tfrecord_file))
        else:
            if self.context_name == context.frame.context.name:
                self.out_lines.append('Files {} and {} have same frame context names\n'.format(self.tfrecord_file, context.tfrecord_file))
            self.tfrecord_file = context.tfrecord_file
        self.context_name = context.frame.context.name

    def save(self, f):
        f.writelines(self.out_lines)

