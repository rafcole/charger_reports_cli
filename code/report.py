import sys
import math
from models import Station, Charger, AvailabilityReport


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

                if len(parts) != 4:
                    print(f"ERROR: Invalid Availablity Report inputs - {parts}")
                    sys.exit(1)

                station_id = parts[0]
                start = parts[1]
                end = parts[2]
                available = parts[3]
                charger_availability.append((station_id, start, end, available))
        return stations, charger_availability

    @classmethod
    def populate_stations(cls, station_data):
        for line in station_data:
            station_id = line[0]
            chargers = line[1:]

            new_station = Station(station_id)

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

            if not AvailabilityReport.is_valid_time_input(
                start_time
            ) or not AvailabilityReport.is_valid_time_input(end_time):
                raise sys.exit(
                    f'ERROR: invalid time stamp - either "{start_time}" or "{end_time}"'
                )

            start_time = int(start_time)
            end_time = int(end_time)

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

            up_time_to_total_time = 0

            if total_reporting_duration > 0:
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
