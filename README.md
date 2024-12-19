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
  - Initially I'd thought to only retain the "up: true" reports. It made the code less maintainable
  - Insertion order is only maintained for the Reports of a given Charger. This is done on the charger level and not the station level in order to reduce the size of the data set being inserted to. Maintaining report order was done to check for timestamp collisions (eg 30-50 && 40-60 from the same charger). I almost left these checks out because of the additional compute required. There are other ways to defend against collisions without the insert complexity - eg checking that the sum of all added Reports don't exceed the reporting duration of the first and last timestamps of a charger. If Chargers report an overwhelming percentage of the time, then this duration check might be sufficient. On the other hand, the assets at hand are so expensive that a little extra compute to catch a malfunction is not a deal breaker.
    - If I were to refactor I'd consider using the interval merging logic for processing a Charger's AvaliabilityReports, rather than maintaining a sorted order. There's an example of this in `Report.calculate_uptime` and it could be extended to `AvailabilityReports` class. This would reduce the number of timestamps each report set has to validate against. This strategy would also allow for significantly lower memory usage and may allow for the elimination of the AvaliabilityReport class all together.
  - Other sorting operation are performed just before processing, reasoning that sorting a large batch is more performant than continuous ordered insertions

Nitpicks

- Availability reports with the same start and end time stamp do not cause an error on their own. They can however cause a collision. See 'zero_time_stamp.txt' and 'time_stamp_same.txt' for this behavior. Given that the prompt requests floored math I'd imagine the potential rounding errors is not relevant to the exercise. That said - if a piece of equipment was submitting zero length reports, I'd want it to show up in the alarming/logs so I intentionally landed on the safe side for this decision.
- Leading zeros aren't accounted for in Charger IDs. 001001 is treated the same as 1001.


Assumptions
- Multiple [Station] entries with the same ID is an error
  - Whereas multiple Report entries per charger is expected behavior, I've decided that repeated station IDs will throw an error. It'd be reasonable that multiple Station entries with the same ID simply add more chargers but without a product team to talk to I made a conservative decision
- Scaling
  - Sorting operations are performed on the smallest reasonable subsets.