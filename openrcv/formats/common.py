
import sys

from openrcv.streams import FileResource, StandardResource


class FormatWriter(object):

    def __init__(self, output_dir=None, stdout=None):
        if stdout is None:
            stdout = sys.stdout
        self.output_dir = output_dir
        self.stdout = stdout

    def make_output_info(self, info_funcs):
        """
        Arguments:
          info_funcs: a single function or an iterable of functions (one
            for each file that needs to be written).  Each function should
            return a 2-tuple of strings: (output_path, file_encoding).
        """
        try:
            iter(info_funcs)
        except TypeError:
            info_funcs = (info_funcs, )
        output_dir = self.output_dir
        stream_resources = []
        output_paths = []
        for func in info_funcs:
            if not output_dir:
                stream_resource = self.stdout_info()
            else:
                output_path, encoding = func()
                stream_resource = FileResource(output_path, encoding=encoding)
                # Only add an output path when not writing to stdout.
                output_paths.append(output_path)
            stream_resources.append(stream_resource)
        return stream_resources, output_paths

    def stdout_info(self):
        """Return a StreamInfo object for stdout."""
        return StandardResource(self.stdout)

    # TODO: get all the FormatWriter classes using this method.
    def write_output(self, info_func, *args, **kwargs):
        """
        Arguments:
          info_func: TODO.
        """
        file_funcs, write_func = info_func()
        stream_resources, output_paths = self.make_output_info(file_funcs)
        args = list(stream_resources) + list(args)
        write_func(*args)
        return output_paths
