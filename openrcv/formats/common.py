
import sys

from openrcv.utils import FileWriter, PathInfo, PermanentFileInfo


class FormatWriter(object):

    def __init__(self, output_dir=None, stdout=None):
        if stdout is None:
            stdout = sys.stdout
        self.output_dir = output_dir
        self.stdout = stdout

    def make_output_info(self, info_funcs):
        try:
            iter(info_funcs)
        except TypeError:
            info_funcs = (info_funcs, )
        output_dir = self.output_dir
        stream_infos = []
        output_paths = []
        for func in info_funcs:
            if not output_dir:
                stream_info = self.stdout_info()
            else:
                output_path, encoding = func()
                stream_info = PathInfo(output_path, encoding=encoding)
                # Only add an output path when not writing to stdout.
                output_paths.append(output_path)
            stream_infos.append(stream_info)
        return stream_infos, output_paths

    def stdout_info(self):
        """Return a StreamInfo object for stdout."""
        return PermanentFileInfo(self.stdout)
