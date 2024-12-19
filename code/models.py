from validation import ValidationUtils
import bisect
import sys


class Charger:
    instances = {}

    def __init__(self, id, station_id):
        if not __class__.is_valid_id(id):
            raise sys.exit(f'ERROR: invalid charger ID "{id}"')

        id = int(id)

        if id in self.__class__.instances:
            raise sys.exit(f'Error: A charger with the ID "{id}" already exists')
        self.__class__.instances[id] = self

        self.id = id
        self.station_id = station_id
        self.availability_reports = []

        self.first_report_timestamp = None
        self.last_report_timestamp = None

        self.total_reported_time = 0

    @property
    def total_reported_time(self):
        return self._total_reported_time

    @total_reported_time.setter
    def total_reported_time(self, total_reported_time):
        self._total_reported_time = total_reported_time

    @classmethod
    def is_valid_id(cls, id):
        return ValidationUtils.is_usable_as_unsigned_int(id, num_bits=64)

    @classmethod
    def get(cls, charger_id):
        charger_id = int(charger_id)
        # todo - validate stationID
        if charger_id not in cls.instances:
            raise Exception(f'Error: Charger "{charger_id}" not found')

        return cls.instances[charger_id]

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def station_id(self):
        return self._station_id

    @station_id.setter
    def station_id(self, station_id):
        self._station_id = station_id

    @property
    def first_report_timestamp(self):
        return self._first_report_timestamp

    @first_report_timestamp.setter
    def first_report_timestamp(self, nano):
        self._first_report_timestamp = nano

    @property
    def last_report_timestamp(self):
        return self._last_report_timestamp

    @last_report_timestamp.setter
    def last_report_timestamp(self, nano):
        self._last_report_timestamp = nano

    @property
    def duration(self):
        return self.last_report_timestamp - self.first_report_timestamp

    @property
    def availability_reports(self):
        return self._availability_reports

    @availability_reports.setter
    def availability_reports(self, data):
        self._availability_reports = data

    def insert_report(self, report):
        # keep sorted order, will be necessary for checking for collisions
        index = bisect.bisect_left(self.availability_reports, report)

        if (
            # check neighboring reports for overlap
            (
                index > 0
                and self.availability_reports[index - 1].stop_time > report.start_time
            )
            or (
                index < len(self.availability_reports)
                and self.availability_reports[index].start_time < report.stop_time
            )
        ):
            sys.exit(
                f"ERROR: Report collision detected for charger {self.id}. "
                f"New report [{report.start_time}, {report.stop_time}] conflicts with an existing report at the same charger"
            )

        self.availability_reports.insert(index, report)

    def add_report(self, start_time, end_time, up):
        report = AvailabilityReport(self.id, start_time, end_time, up)

        self.insert_report(report)

        # update min/max timestamps
        if (
            self.first_report_timestamp is None
            or report.start_time < self.first_report_timestamp
        ):
            self.first_report_timestamp = report.start_time
        if (
            self.last_report_timestamp is None
            or report.stop_time > self.last_report_timestamp
        ):
            self.last_report_timestamp = report.stop_time

        self.total_reported_time += end_time - start_time

        if (
            self.total_reported_time
            > self.last_report_timestamp - self.first_report_timestamp
        ):
            raise sys.exit(
                f"ERROR: Cumulative Avaliability Report duration for charger {self.id} exceeds 100% of reporting time period"
            )

    def reports_by_status(self, available_bool):
        return [
            report
            for report in self.availability_reports
            if report.up == available_bool
        ]

    def reports_by_start_time(self):
        return sorted(self.availability_reports, key=lambda p: p.start_time)

    def __str__(self):
        return f"Charger: {self.id}\n\t\t\tassigned to Station {self.station_id}\n\t\t\t availability_reports: {self.availability_reports}"

    def __repr__(self):
        return self.__str__()


class AvailabilityReport:
    instances = {}

    def __init__(self, charger_id, start_time, stop_time, up):
        # start_time
        if not __class__.is_valid_time_input(
            start_time
        ) and __class__.is_valid_time_input(stop_time):
            raise sys.exit(
                f'ERROR: invalid time stamp - either "{start_time}" or "{stop_time}"'
            )

        if not ValidationUtils.is_usable_as_bool(up):
            raise sys.exit(
                f'ERROR: invalid input for Availability Report status boolean - "{up}"'
            )

        if start_time > stop_time:
            raise sys.exit(
                "ERROR: negative reporting duration found in Availability Reports"
            )

        self.charger_id = charger_id
        self.start_time = start_time
        self.stop_time = stop_time
        self.up = up in {"True", "true", "TRUE"}

        self.id = (charger_id, start_time)

    @classmethod
    def is_valid_time_input(cls, val):
        return ValidationUtils.is_usable_as_unsigned_int(val, num_bits=64)

    def duration(self):
        return self.stop_time - self.start_time

    @property
    def charger_id(self):
        return self._charger_id

    @charger_id.setter
    def charger_id(self, charger_id):
        self._charger_id = charger_id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, args):
        self._id = f"{args[0]}{args[1]}"

    def __str__(self):
        return f"Report: Charger: {self.charger_id}, Start: {self.start_time}, Stop: {self.stop_time}, Up: {self.up}\n"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self.start_time < other.start_time


class Station:
    instances = {}

    def __init__(self, id):
        if not __class__.is_valid_id(id):
            raise sys.exit(f'ERROR: invalid station ID "{id}"')

        id = int(id)

        if id in self.__class__.instances:
            raise sys.exit(
                f'Error: Duplicate station ID "{id}" detected, please check inputs'
            )

        self.__class__.instances[id] = self
        self.id = id
        self.chargers = {}
        self.first_report_timestamp = None
        self.last_report_timestamp = None
        self.all_reports = []

    @classmethod
    def is_valid_id(cls, value):
        return ValidationUtils.is_usable_as_unsigned_int(value, num_bits=32)

    @classmethod
    def get(cls, station_id):
        # todo - validate stationID
        if station_id not in cls.instances:
            sys.exit(f'Error: Station "{station_id}" not found')

        return cls.instances[station_id]

    @classmethod
    def get_all(cls):
        return cls.instances

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def chargers(self):
        return self._chargers

    @chargers.setter
    def chargers(self, data):
        self._chargers = data

    def add_charger(self, charger):
        self.chargers[charger.id] = charger

    def __str__(self):
        charger_ids = list(self.chargers.keys())
        return f"Station ID: {self.id}\n\t\t\t\t Chargers: {charger_ids}\n\t\t\t\t\tFirst timestamp: {self.first_report_timestamp}\t\t Last timestamp:{self.last_report_timestamp}\n"

    def __repr__(self):
        return self.__str__()
