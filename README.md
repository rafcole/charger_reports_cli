# charger_reports_cli


Use - from inside ./code
```
python main.py ./relative/path.txt
```

To see the results against some common edgecases, run this bash script
```
for file in *.txt; do echo "Processing file: $file"; python ../../code/main.py "$file"; echo ""; done
```

General Structure

- Stations have Chargers but don't instantiate them internally, in order to keep the classes more loosely coupled. It could be the case that a charger needs to be instantiated before it's assigned to a Station (eg it's on the production line) or perhaps a charger is never assigned to a station (R&D units, trade show demos, etc).
- Chargers do instantiate their own reports. Chargers and Availability Report classes are tightly coupled
- Performance concerns
  - Insertion order is only maintained for the Reports of a given Charger. This is done on the charger level and not the station level in order to reduce the size of the data set being inserted to. Maintaining report order was done to check for timestamp collisions (eg 30-50 && 40-60 from the same charger). I almost left these checks out because of the additional compute required. There are other ways to defend against collisions without the insert complexity - eg checking that the sum of all added Reports don't exceed the reporting duration of the first and last timestamps of a charger. If Chargers report an overwhelming percentage of the time, then this duration check might be sufficient. On the other hand, the assets at hand are so expensive that a little extra compute to catch a malfunction is not a deal breaker.
    - If I were to refactor I'd create an array of merged timestamps to check for collisions (eg, abutting time ranges get combined) to reduce the number of timestamps each report set has to validate against.
  - Other sorting operation are performed just before processing, reasoning that sorting a large batch is more performant than continuous ordered insertions

Nitpicks

- Availability reports with the same start and end time stamp do not cause an error on their own. They can however cause a collision. See 'zero_time_stamp.txt' and 'time_stamp_same.txt' for this behavior. Given that the prompt requests floored math I'd imagine the potential rounding errors is not relevant to the exercise. That said - if a piece of equipment was submitting zero length reports, I'd want it to show up in the alarming/logs so I intentionally landed on the safe side for this decision.


Assumptions
- Multiple [Station] entries with the same ID is an error
  - Whereas multiple Report entries per charger is expected behavior, I've decided that repeated station ID's will be an error for this. It'd be reasonable that multiple Station entries with the same ID simply add more chargers but without a product team to talk to I made a conservative decision
- Scaling
  - Sorting operations are performed on the smallest reasonable subsets.

Initial

Find Station Uptime
  Station uptime - at least one charger avaliable
    Bounds - first timestamp (regardless of status) from station N charger to
      last time stamp from any station N charger
  Down is down
  Unaccounted for time is down
  Are time ranges inclusive?
    Check against input examples
    Inclusive of start time, exclusive of end time
      What if [25:25]? Length = 1? Even possible?



Charger mapping
  {
    charger : {
      id: int,
      assigned station: int,
      global start time: int,
      global end time: int,
      accounted run time: int,
      accounted down time: bool
      entries: [sorted tuples?] (don't sort during stream processing, sort if error processing)
      total down time - derived - find unaccounted time from unaccounted time([start:end] - accounted run time)
      + accounted down time
        want this to be derived so we can know what data set the charger was working with and don't have
        inconsistency between data sets
    }
  }

  {
    station : {
      id: int,
      chargers: int arr for id's,
      start time: int
      end time: int
      accounted run time: int
      accounted down time: bool
      unaccounted run time and total run time are derived
    }
  }

Bounding
  Global station start time - lowest time stamp of any assigned charger start times
  Global station end time - highest time stamp of any assigned charger end time
  Station report time - highest minus lowest
  Accounted run time - running total of all charger timeranges recieved so far
  Unaccounted run time - station report time minus accounted run time


Errors
  Input
    CLI input
      TODO
      No such file
    File format
      TODO
      only .txt?
    File content
      Formatting
        Nothing to garuntee sort order of [Charger Availability Reports] or [Stations ]
        Overlapping time spans per charger [1-4][2-5]
        Conflicting overlaps



      Warnings:
        Unlisted charger in [Charger Availability Reports]
