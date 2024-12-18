import sys
import math
import os


class ValidationUtils:
    @classmethod
    def is_usable_as_unsigned_32_bit_int(cls, value):
        if type(value) is str:
            if not value.isdigit():
                return False
            value = int(value)

        if type(value) is int:
            return 0 <= value <= 2**32 - 1

        return False

    @classmethod
    def is_unsigned_64_bit_integer_as_str(cls, value):
        if value.isdigit():
            num = int(value)
            if 0 <= num <= 2**64 - 1:
                return True
        return False

    @classmethod
    def is_bool(cls, value):
        if type(value) is bool:
            return True

        if type(value) is str:
            return {"True", "true", "TRUE", "False", "false", "FALSE"}.includes(input)
        # todo
        return False


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

    @classmethod
    def is_valid_id(cls, id):
        return ValidationUtils.is_usable_as_unsigned_32_bit_int(id)

    @classmethod
    def get(cls, charger_id):
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

    def add_report(self, start_time, end_time, up):
        report = AvailabilityReport(self.id, start_time, end_time, up)

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

        self.availability_reports.append(report)

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
        self.charger_id = charger_id
        self.start_time = start_time
        self.stop_time = stop_time
        self.up = up

        self.id = (charger_id, start_time)

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
        return ValidationUtils.is_usable_as_unsigned_32_bit_int(value)

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


class Report:
    @classmethod
    def generate(cls, file_path):
        station_data, charger_report_data = cls.extract_data(file_path)
        if len(station_data) == 0:
            print("ERROR: No stations in dataset")
            sys.exit(1)
        if len(charger_report_data) == 0:
            print("ERROR: No availability reports in dataset")
            sys.exit(1)

        cls.populate_stations(station_data)
        cls.populate_charger_reports(charger_report_data)
        cls.print_to_std_out(cls.summarize_uptime())

    @classmethod
    def extract_data(cls, file_path):
        stations = []
        charger_availability = []

        with open(file_path, "r") as file:
            lines = file.readlines()

        current_section = None

        for line in lines:
            line = line.strip()

            if len(line) == 0:
                continue

            if line.startswith("[") and line.endswith("]"):
                current_section = line.strip("[]")
                continue

            if current_section == "Stations":
                parts = line.split()

                stations.append(parts)

            elif current_section == "Charger Availability Reports":
                parts = line.split()
                station_id = int(parts[0])
                start = int(parts[1])
                end = int(parts[2])
                available = parts[3].lower() == "true"
                charger_availability.append((station_id, start, end, available))
        return stations, charger_availability

    @classmethod
    def populate_stations(cls, station_data):
        print(station_data)
        for line in station_data:
            station_id = line[0]
            chargers = line[1:]  # TODO test against stations with no assigned chargers

            new_station = Station(station_id)

            # check for station uniqueness
            # redundant with erroring in station initialization
            for charger_id in chargers:
                new_charger = Charger(charger_id, new_station.id)
                new_station.add_charger(new_charger)
        if len(Charger.instances) == 0:
            print("ERROR: No chargers in dataset")
            sys.exit(1)

    @classmethod
    def populate_charger_reports(cls, report_data):
        for line in report_data:
            charger_id, start_time, end_time, up = line
            charger = None
            try:
                charger = Charger.get(charger_id)
            except Exception as e:
                print(
                    f"{e}\nError: Charger {charger_id} found in avaliability reports but not associated with a station"
                )
                sys.exit(1)

            charger.add_report(start_time, end_time, up)

    @classmethod
    def print_to_std_out(cls, data):
        for station_id, percent in data:
            floored_percent = math.floor(percent * 100)
            print(f"{str(station_id)} {floored_percent}")

    @classmethod
    def summarize_uptime(cls):
        report_data = []
        sorted_station_ids = sorted(Station.get_all().keys())

        for station_id in sorted_station_ids:
            current_station = Station.get(station_id)
            station_chargers = list(current_station.chargers.values())

            # skip stations with no chargers
            if len(station_chargers) == 0:
                continue

            station_reports = []

            first_time_stamp = None
            last_time_stamp = None

            for charger in station_chargers:
                # skip chargers with no reports
                if len(charger.availability_reports) == 0:
                    continue

                # update station timestamps against the charger timestamps
                if (
                    first_time_stamp is None
                    or charger.first_report_timestamp < first_time_stamp
                ):
                    first_time_stamp = charger.first_report_timestamp
                if (
                    last_time_stamp is None
                    or charger.last_report_timestamp > last_time_stamp
                ):
                    last_time_stamp = charger.last_report_timestamp

                # perform up time calculations on only up_time reports
                station_reports.extend(charger.reports_by_status(available_bool=True))

            up_time, down_time = cls.calculate_uptime(station_reports)
            total_reporting_duration = last_time_stamp - first_time_stamp

            up_time_to_total_time = up_time / total_reporting_duration

            report_data.append((station_id, up_time_to_total_time))
        return report_data

    @classmethod
    def calculate_uptime(cls, reports_list):
        if not reports_list:
            return 0, 0

        reports_list = sorted(reports_list)

        merged = []
        up_time_total = 0
        unaccounted_time_total = 0

        merged_start, merged_end = reports_list[0].start_time, reports_list[0].stop_time

        for report in reports_list[1:]:
            current_start = report.start_time
            current_end = report.stop_time

            if current_start > merged_end:  # Gap detected
                unaccounted_time_total += current_start - merged_end
                merged.append((merged_start, merged_end))
                up_time_total += merged_end - merged_start
                merged_start, merged_end = current_start, current_end
            else:  # Merge overlapping/adjacent ranges
                merged_end = max(merged_end, current_end)

        # Add the last range
        merged.append((merged_start, merged_end))
        up_time_total += merged_end - merged_start

        return up_time_total, unaccounted_time_total

        """
        Get station keys
        Sort ascending

        Iterate over keys/stations
          Calculate up time HELPER TODO
          Print to screen
        """


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    Report.generate(file_path)


if __name__ == "__main__":
    main()


# disjuncture in that report come in at the charger level (perhaps each charger has it's own 5g system)
# but the station data is not associated
# Cumulative up time reports are organized at the station level
# now we need to mimic some kind of join table functionality


# Tracking the first/last charger time stamps of a station adds O(n)
# The avaliablity reports can be lightly parsed to see if the new time stamps exceed the start and end times
# For the sake of this report we only need to track up time, so down time can be used to check against station
# start and end times but does not need to be included in amongst up time reports.

# report_data = ingest_report(file_path)


"""
Validation of inputs
  Inpute are validated in the processing phase of the Report class. This creates a tight coupling between the




collision reporting
  The use of combo id for reports (chargerid + starttime) is meant to detect duplicate entries
  Overlapping reports from the same charger are not directly solved for
    This would add O(m) (where m is the number of reports to a given charger) to the processing
    of each report
    On a large dataset this check could be swapped to a computational check - has any charger reported more time than is possible given it's minimum start time and maximum end time? This would not catch all instances


This system could be optimized for stream processing. Greater attention would be paid to maintaining rolling averages and creating snapshots. The program as written is more oriented towards batch processing, as alluded to in the prompt.

given an input file

Create a report object

allStations = { station_id: [charger_id, charger_id ... ] }
allChargers = { charger_id: [AvailabilityReport, AvailabilityReport, AvailabilityReport] }

Iterate over [Stations] report section
  For each line, create Station N
  For each entry following Station N
    Add charger_id to Station N
    Add charger to allChargers
  Add Station N to report


Iterate over Charger Availability reports
  Charger availability reports NOT GUARUNTEED IN ORDER
    Must be resilient to out of order entries for both charger ID and time range
  Add availability report to station
    Update station start end times (maybe only for downtime reports, we won't be )




Chargers should be able to generate summaries of their availability reports
Stations should be able to generate summaries of their charger reports
  Create sorted
    Sorted by start_time
      merge + report gaps (see helper function)
      compare uptime bounds to total reporting bounds to check for bookended failures reported by chargers


Reports should be able to format and output station summaries

Prompt lends itself to a naive sort of 'all at once' processing
What we'd really want to do is optimize for stream processing
  IE be able to integrate charger availability reports on the fly
    Integrate into summaries, update rolling averages
    If downtime detected, throw error
    Risks race conditions, would need protection for transaction/consistency guaruntees
  Inserting into ordered list is O(log n), which is slower than simply adding another entry
  and sorting all at once

Unclear
  Is the edge between two availability reports considered contiguos? Eg [0:50] && [50:100]
  This report optimizes for reporting uptime
    Would be more computationally expensive to drill down into unreported downtime

Validations skipped
  Charger end time < charger start time




[--------------]
                       [---------]


[--------------]
               [---------]


    [------]
[--------------]



      [--------------]
    [---------]
^ not possible on a station basis, no positive start time

   [--------------]
 [---------]
[--------------]
[--------------------------]



[--------------]
[---------]
[--------------]
[--------------------------]



[--------------]
[---------]
                  [--------------]
[--------------------------]


[--------------]
               [---------]
                         [--------------]
[--------------------------]

  [--------------]
  [---------]
  [--------------]
[--------------------------]


"""
