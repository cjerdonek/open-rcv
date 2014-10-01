
from openrcv.models import ContestInfo
from openrcv.utils import FILE_ENCODING, log, time_it


class Parser(object):

    # TODO: reinitialize these when parsing a new file.
    line_no = 0
    line = None

    def iter_lines(self, f):
        """
        Return an iterator over the lines of an input file.

        Each iteration sets self.line and self.line_no.

        """
        for line_no, line in enumerate(iter(f), start=1):
            self.line = line
            self.line_no = line_no
            yield line
        log("parsed: %d lines" % line_no)

    def get_parse_return_value(self):
        return None

    def parse_lines(self, lines):
        raise NotImplementedError()

    def parse_file(self, f):
        with time_it("parsing %r" % self.name):
            log("parsing...\n  %r" % self.name)
            lines = self.iter_lines(f)
            try:
                self.parse_lines(lines)
            except:
                raise Exception("error while parsing line %d: %r" %
                                (self.line_no, self.line))
        return self.get_parse_return_value()

    def parse_path(self, path):
        log("opening...\n  %s" % path)
        with open(path, "r", encoding=FILE_ENCODING) as f:
            return self.parse_file(f)


class BLTParser(Parser):

    name = "BLT file"

    def get_parse_return_value(self):
        return self.info

    def parse_int_line(self, line):
        """Return a generator of integers."""
        return (int(s) for s in line.split())

    def parse_next_line_text(self, lines):
        return next(lines).strip()

    def parse_next_line_ints(self, lines):
        return self.parse_int_line(next(lines))

    def parse_ballot_lines(self, lines):
        ballot_count = 0
        for line in lines:
            ballot_numbers = self.parse_int_line(line)
            weight = next(ballot_numbers)
            print("weight: %r" % weight)
            if weight == 0:
                break
            ballot_count += 1
            print(tuple(ballot_numbers))
        return ballot_count

    def parse_lines(self, lines):
        info = ContestInfo()
        self.info = info

        # First line.
        candidate_count, seat_count = self.parse_next_line_ints(lines)
        info.seat_count = seat_count

        # Withdrawn candidates.
        withdraw_numbers = self.parse_next_line_ints(lines)
        withdrawn = []
        for number in withdraw_numbers:
            assert number < 0
            withdrawn.append(-1 * number)
        info.withdrawn = withdrawn

        ballot_count = self.parse_ballot_lines(lines)
        info.ballot_count = ballot_count

        # Read candidate list.
        candidates = []
        for i in range(candidate_count):
            name = self.parse_next_line_text(lines)
            candidates.append(name)

        name = self.parse_next_line_text(lines)
        info.name = name
        # TODO: assert remaining lines empty.
        # TODO: and add test that these asserts work.
