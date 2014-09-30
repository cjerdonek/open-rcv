
class ContestInfo(object):

    """
    Attributes:
      name: name of contest.
      seat_count: integer number of winners.

    """

    ballot_count = 0

    def __init__(self):
        pass

    # TODO: look up the proper return type.
    def __repr__(self):
        return self.name
