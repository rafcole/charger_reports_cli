import re
import pprint
import sys

class Charger:
    def __init__(self, id, station_id):
        self.id = id
        self.station_id = station_id
        self.availabilityReports = []

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

    def add_report(self, report):
        self.availabilityReports.append(report)

    def __str__(self):
        return f'Charger: {self.id}\n\t\t\tassigned to Station {self.station_id}\n\t\t\t AvailabilityReports: {self.availabilityReports}'

    def __repr__(self):
        return self.__str__()


class AvailabilityReport:
  def __init__(self, charger_id, start, stop, up):
    self.charger_id = charger_id
    self.start_time = start
    self.stop_time = stop
    self.up = up

  def duration(self):
      return self.stop_time - self.start_time

  @property
  def charger_id(self):
      return self._charger_id

  @charger_id.setter
  def charger_id(self, charger_id):
      self._charger_id = charger_id

  def __str__(self):
      return f'Report: Charger: {self.charger_id}, Start: {self.start_time}, Stop: {self.stop_time}, Up: {self.up}\n'

  def __repr__(self):
      return self.__str__()


class Station:

    instances = {}

    def __init__(self, id):
        if id in self.__class__.instances:
            raise sys.exit(f'Error: Duplicate station ID "{id}" detected, please check inputs')

        self.id = id
        self.chargers = {}
        self.first_report_timestamp = None
        self.last_report_timestamp = None
        self.charger_up_reports = [] # feels bad, not sure station should know about it
        self.__class__.instances[id] = self

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

    @property
    def first_report_timestamp(self):
        return self._first_report_timestamp
    @first_report_timestamp.setter
    def first_report_timestamp(self, nano):
        self._first_report_timestamp = nano

    def add_report(self, report):
        if self.first_report_timestamp is None or report.start_time < self.first_report_timestamp:
            self.first_report_timestamp = report.start_time
        if self.last_report_timestamp is None or report.stop_time > self.last_report_timestamp:
            self.last_report_timestamp = report.stop_time

        if report.up:
            self.charger_up_reports.append(report)



    @property
    def last_report_timestamp(self):
        return self._last_report_timestamp
    @last_report_timestamp.setter
    def last_report_timestamp(self, nano):
        self._last_report_timestamp = nano

    @property
    def duration(self):
        return self.last_report_timestamp - self.first_report_timestamp

    def add_charger(self, charger):
        self.chargers[charger.id] = charger

    def __str__(self):
        charger_ids = list(self.chargers.keys())
        return f'Station ID: {self.id}\n\t\t\t\t Chargers: {charger_ids}'

    def __repr__(self):
        return self.__str__()


    # def print(self):
    #     print(f'Station: {self.id}   Chargers: {self.chargers}')


class Report:
    def __init__(self):
        self.stations = {}
        self.downTime = 0.0

    @property
    def stations(self):
        return self._stations

    @stations.setter
    def stations(self, arrayOfStations):
        self._stations = arrayOfStations

    def addStation(self, station_id):
        self.stations[station_id] = Station(station_id)

        return self._stations[station_id]

read_data = ''


allStations = {}
allChargers = {}

#TODO - filepath is cli arg

file_path = '../coding-challenge-charger-uptime-main/input_1.txt'

def ingest_report(file_path):
  in_stations_section = False
  in_charger_reports = False

  all_stations = {}
  all_chargers = {}

  with open(file_path, 'r') as file:
      for line in file:
          line = line.strip()

          # Check for section headers
          if line == "[Stations]":
              in_stations_section = True
              continue
          elif line == "[Charger Availability Reports]":
              continue
          elif len(line) == 0:
              in_stations_section = False
              continue

          # Create station, add chargers
          # TODO - allow duplicative charger entries
          if in_stations_section and line:
              line_data = line.split()
              station_id = line_data[0]
              current_station = Station(station_id)
              all_stations[station_id] = current_station #now duplicative of Station.instances

              charger_ids = line_data[1:]

              for id in charger_ids:
                  new_charger = Charger(id, station_id)
                  all_chargers[id] = new_charger
                  current_station.add_charger(new_charger)

                  # print(new_charger)
          # parse reports
          else:
              # print(line)
              report_entities = line.split()
              charger_id = report_entities[0]
              # print(type(charger_id))
              start_time = report_entities[1]
              stop_time = report_entities[2]
              up = report_entities[3]

              report = AvailabilityReport(charger_id, start_time, stop_time, up)

              parent_station = all_stations[all_chargers[charger_id].station_id]
              parent_station.add_report(report)

              # all_chargers[charger_id].add_report(report)

              # print(current_station)
              # print(f"Station ID: {station_id}, Chargers: {charger_ids}")

  return {
      'stations': Station.instances,
      'chargers': all_chargers
      }

# disjuncture in that report come in at the charger level (perhaps each charger has it's own 5g system)
# but the station data is not associated
# Cumulative up time reports are organized at the station level
# now we need to mimic some kind of join table functionality

# Tracking the first/last charger time stamps of a station adds O(n)
# The avaliablity reports can be lightly parsed to see if the new time stamps exceed the start and end times
# For the sake of this report we only need to track up time, so down time can be used to check against station
# start and end times but does not need to be included in amongst up time reports.

report_data = ingest_report(file_path)

pprint.pprint(report_data)

for station_key in report_data['stations']:
    print(station_key)
    # print(type(station))

"""
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



