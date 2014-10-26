
"""
Extensions to the argparse module.

"""

class Option(tuple):
    """
    Encapsulates a command option (e.g. "-h" and "--help", or "--run-tests").

    """
    def display(self, glue):
        return glue.join(self)
