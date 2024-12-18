# charger_reports_cli


Use - from inside ./code
```
python main.py ./relative/path.txt
```


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
