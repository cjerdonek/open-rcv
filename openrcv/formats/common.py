
import sys

from openrcv.utils import FileWriter, PathInfo, PermanentFileInfo


class FormatWriter(object):

    def __init__(self, output_dir=None, stdout=None):
        if stdout is None:
            stdout = sys.stdout
        self.output_dir = output_dir
        self.stdout = stdout

    def get_output_info(self, get_file_info):
        output_dir = self.output_dir
        output_paths = []
        if not output_dir:
            stream_info = self.stdout_info()
        else:
            output_path, encoding = get_file_info()
            stream_info = PathInfo(output_path, encoding=encoding)
            output_paths.append(output_path)
        return stream_info, output_paths

    def stdout_info(self):
        """Return a StreamInfo object for stdout."""
        return PermanentFileInfo(self.stdout)
