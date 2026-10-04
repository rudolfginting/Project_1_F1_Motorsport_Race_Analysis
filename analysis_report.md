# 2024 F1 Motorsport Race Analysis

## 1. Project Overview

This project analyzes Formula 1 race data from the 2024 season using Python, pandas, NumPy, Matplotlib, and FastF1.

The main objectives are:

1. Analyze driver finishing performance.
2. Examine recorded lap-time patterns.
3. Compare driver pace relative to other drivers on the same lap.
4. Analyze lap-time consistency.
5. Examine tyre usage and tyre age.
6. Investigate the relationship between tyre age and relative pace.
7. Apply weighted statistical analysis to the tyre-age relationship.

The project uses race-result and lap-level data collected from FastF1.

### Dataset

* Season: 2024
* Race weekends: 24
* Raw race-result records: 479
* Raw lap records: 26,604
* Clean lap records used in the main analyses: 24,399

The raw lap dataset contains information such as:

* Driver
* Team
* Race
* Lap number
* Lap time
* Stint
* Tyre compound
* Tyre life
* Fresh tyre status
* Track status
* Pit-in / pit-out information

---

# 2. Data Collection

FastF1 was used to retrieve the 2024 race-session data.

The data collection pipeline loads race sessions and extracts both:

* race-result information
* lap-level information

Lap-level data was explicitly enabled during loading because the project requires lap-time, tyre, and stint analysis.

The resulting raw datasets were stored as:

data/raw/race_results_2024.csv
data/raw/race_laps_2024.csv

The complete 2024 season produced 26,604 raw lap records.

---

# 3. Data Cleaning

Before analysis, lap-time values were converted from time-duration format into seconds.

Only observations containing valid:

* lap time
* driver
* lap number

were retained.

For the main pace analysis, extreme lap times were removed using the 1st and 99th percentiles.

Pit-entry and pit-exit laps were excluded from the relative-pace analyses because these laps can contain abnormal timing caused by entering or leaving the pit lane.

Race names were also normalized to reduce inconsistencies caused by whitespace differences.

After cleaning:

Raw lap records:   26,604
Clean lap records: 24,399

For the controlled relative-pace analysis, 24,367 comparable lap observations remained after requiring sufficient driver coverage for each race-lap comparison.

---

# 4. Average Finishing Position

The first analysis examines average finishing position for each driver.

The calculation groups race-result records by driver and calculates:

* number of recorded race results
* average finishing position
* total championship points

The drivers with the lowest average finishing positions in this dataset included:

| Driver          | Recorded races | Average finish | Points |
| --------------- | -------------: | -------------: | -----: |
| Max Verstappen  |             24 |          3.625 |    399 |
| Lando Norris    |             24 |          4.292 |    344 |
| Charles Leclerc |             24 |          4.542 |    327 |
| Oscar Piastri   |             24 |          5.125 |    265 |
| Carlos Sainz    |             23 |          5.696 |    262 |
| George Russell  |             24 |          6.750 |    226 |
| Lewis Hamilton  |             24 |          6.958 |    207 |

The complete output is stored in:

data/processed/driver_finish_summary.csv

### Interpretation

Average finishing position describes race outcomes, but it is not a pure measurement of driver ability.

Race results are affected by factors including:

* car performance
* reliability
* strategy
* pit stops
* incidents
* safety cars
* traffic
* race conditions

The number of recorded races must also be considered. For example, drivers with only one to three recorded races should not be directly interpreted in the same way as drivers with 24 race observations.

---

# 5. Recorded Lap-Time Analysis

The second analysis calculates recorded lap-time statistics for each driver.

The main metrics are:

* mean lap time
* median lap time
* standard deviation
* number of recorded laps

The output is stored in:

data/processed/driver_lap_pace_summary.csv

### Important limitation

Raw lap times from different circuits cannot be directly interpreted as a universal driver-speed ranking.

Different circuits have different:

* track lengths
* layouts
* corner characteristics
* weather conditions
* tyre demands
* fuel loads
* traffic conditions
* race strategies

Therefore, the raw average lap-time analysis is primarily exploratory.

This limitation motivated the development of the relative-pace analysis.

---

# 6. Lap-Time Consistency

Lap-time standard deviation was used as a simple measure of variation in recorded lap times.

A lower standard deviation indicates that the recorded lap times are more tightly distributed around the driver's mean lap time.

The output is stored in:

data/processed/driver_consistency_summary.csv

However, lap-time standard deviation should not be interpreted as a complete measure of driving consistency.

Variation can also come from:

* traffic
* tyre condition
* fuel load
* track evolution
* weather
* pit stops
* safety-car periods
* different circuit characteristics

Therefore, this metric is treated as descriptive rather than definitive.

---

# 7. Tyre Usage

The project also analyzes the number of recorded laps by tyre compound.

The results were:

| Compound     | Recorded laps |
| ------------ | ------------: |
| HARD         |        13,289 |
| MEDIUM       |         8,638 |
| INTERMEDIATE |         2,136 |
| SOFT         |         1,759 |
| WET          |            31 |

The output is stored in:

data/processed/tyre_usage_summary.csv

HARD and MEDIUM accounted for most of the recorded dry-weather laps in the cleaned dataset.

However, tyre-lap counts alone cannot determine which compound was faster or which strategy was more effective.

---

# 8. Championship Points

Championship points were analyzed separately from lap-time metrics.

The highest point totals in the dataset included:

| Driver          | Points |
| --------------- | -----: |
| Max Verstappen  |    399 |
| Lando Norris    |    344 |
| Charles Leclerc |    327 |
| Oscar Piastri   |    265 |
| Carlos Sainz    |    262 |
| George Russell  |    226 |
| Lewis Hamilton  |    207 |
| Sergio Perez    |    138 |

The output is stored in:

data/processed/driver_points_summary.csv

Championship points represent accumulated race outcomes under the Formula 1 scoring system. They should therefore not be treated as a direct measurement of raw lap pace.

---

# 9. Relative Pace Analysis

To address the problem of comparing raw lap times across different circuits, the project introduced a relative-pace metric.

For each race and lap, the lap time was compared with the median lap time recorded for that same race and lap.

The basic calculation was:

Relative lap time =
Driver lap time − Race-lap reference time

A negative value indicates that the driver's lap was faster than the reference.

A positive value indicates that the driver's lap was slower than the reference.

The output is stored in:

data/processed/driver_relative_pace_summary.csv

This approach reduces the influence of differences in circuit length and layout because drivers are compared within the same race and lap context.

---

# 10. Race-by-Race Relative Pace

The next analysis preserved the race dimension instead of aggregating the entire season immediately.

For each race and driver, the project calculated:

* number of comparable laps
* mean relative pace
* median relative pace

The output files are:

data/processed/race_driver_relative_pace.csv
data/processed/race_relative_pace_matrix.csv

This allows driver pace to be examined on a race-by-race basis rather than assuming that a season-wide average represents every circuit equally.

---

# 11. Tyre Age and Relative Pace

The project then investigated whether tyre age was associated with changes in relative pace.

`TyreLife` represents the number of laps completed on the current tyre.

The first version grouped observations by:

Compound + TyreLife

and calculated relative-pace statistics.

This analysis showed that HARD tyre observations generally moved from negative relative pace at lower tyre ages toward positive relative pace at higher tyre ages.

However, the result could still be affected by differences between drivers and by the conditions under which tyres were used.

Therefore, a more controlled comparison was developed.

---

# 12. Controlled Tyre-Age Relative Pace

The controlled analysis compared drivers within the same:

Race + Lap

rather than comparing raw lap times across different races.

For each race-lap combination, a minimum of five drivers was required.

The reference pace for each driver was calculated using a leave-one-out approach so that the driver's own lap was excluded from their comparison reference.

This produced:

Comparable lap observations: 24,367

The output is stored in:

data/processed/controlled_tyre_age_relative_pace.csv

This provides a more controlled measure of whether a driver's lap was relatively fast or slow compared with other drivers experiencing the same race-lap environment.

---

# 13. Exploratory Tyre Degradation Trend

A linear regression was then applied to the aggregated controlled tyre-age data.

The purpose was to investigate whether relative pace changed systematically as tyre life increased.

The initial unweighted analysis produced:

| Compound     |    Slope | Correlation |
| ------------ | -------: | ----------: |
| SOFT         | -0.01173 |      -0.168 |
| INTERMEDIATE | -0.00549 |      -0.115 |
| HARD         | +0.01836 |      +0.472 |
| MEDIUM       | +0.02069 |      +0.799 |

This analysis was treated as exploratory because each `TyreLife` point was initially given equal weight even though some points represented many more laps than others.

---

# 14. Weighted Tyre-Age Analysis

To improve the analysis, the project introduced lap-count weighting.

Each `TyreLife` observation was weighted according to the number of laps represented by that observation.

The weighted analysis produced:

| Compound     | TyreLife points | Total laps |    Slope | Weighted correlation |
| ------------ | --------------: | ---------: | -------: | -------------------: |
| INTERMEDIATE |              31 |      1,854 | -0.01285 |               -0.218 |
| SOFT         |              21 |      1,545 | +0.00384 |               +0.058 |
| MEDIUM       |              34 |      7,898 | +0.02244 |               +0.747 |
| HARD         |              49 |     12,386 | +0.02727 |               +0.820 |

The output is stored in:

data/processed/weighted_tyre_degradation_trend.csv

The figure is stored in:

outputs/figures/12_weighted_tyre_degradation_trend.png

---

# 15. Interpretation of the Weighted Analysis

The strongest positive relationships in this analysis were observed for HARD and MEDIUM compounds.

HARD produced:

Slope:                 +0.02727
Weighted correlation:  +0.820
Total laps:             12,386

MEDIUM produced:

Slope:                 +0.02244
Weighted correlation:  +0.747
Total laps:              7,898

These results indicate a positive statistical association between tyre age and relative lap time for HARD and MEDIUM observations in this dataset.

In practical terms, as `TyreLife` increased, relative lap time tended to become more positive for these compounds.

SOFT showed almost no linear relationship:

Slope:                +0.00384
Weighted correlation: +0.058

INTERMEDIATE showed a weak negative relationship:

Slope:                -0.01285
Weighted correlation: -0.218

The different behavior of INTERMEDIATE and SOFT demonstrates that tyre-age effects cannot simply be represented by one common linear model across every compound.

---

# 16. Important Statistical Limitation

The slope values should **not** be interpreted as exact physical tyre-degradation rates.

For example:

HARD = +0.02727 seconds per tyre-life lap

does not mean that an F1 HARD tyre physically loses exactly 0.02727 seconds of performance after every lap.

The slope represents the statistical relationship observed in this dataset.

Other factors can influence relative pace, including:

* fuel load
* circuit characteristics
* track evolution
* weather
* traffic
* safety cars
* tyre compound
* race strategy
* driver behavior
* vehicle performance

Therefore, the appropriate interpretation is:

> The analysis found a positive association between tyre age and relative pace for HARD and MEDIUM compounds.

It should not be described as a definitive causal measurement of tyre degradation.

---

# 17. Why the Controlled Analysis Matters

One of the main methodological improvements in this project was moving from raw lap-time comparison toward within-race relative comparison.

The progression was:

Raw lap time
      ↓
Clean lap time
      ↓
Race-normalized relative pace
      ↓
Race-by-race relative pace
      ↓
Tyre-age relative pace
      ↓
Controlled leave-one-out comparison
      ↓
Weighted tyre-age trend

This progression demonstrates that the project was not simply producing charts from a dataset.

Each stage addressed a limitation discovered in the previous stage.

---

# 18. Limitations

Several limitations remain.

### 18.1 Observational data

The analysis is based on race-session observations rather than controlled experiments.

Therefore, statistical association does not establish causation.

### 18.2 Confounding variables

Tyre age is correlated with many race conditions.

For example, a high tyre age may occur during a long stint, while a low tyre age may occur immediately after a pit stop.

Those situations can have very different fuel loads and race contexts.

### 18.3 Compound differences

HARD, MEDIUM, SOFT, INTERMEDIATE, and WET tyres are designed and used under different conditions.

A single degradation model is therefore inappropriate for all compounds.

### 18.4 Small samples at high tyre ages

Some high `TyreLife` values contain considerably fewer observations than the central part of the distribution.

Results at very high tyre ages should therefore be interpreted cautiously.

### 18.5 Relative reference

Relative pace depends on the drivers available in a particular race-lap comparison.

Changes in the set of participating drivers can affect the reference distribution.

---

# 19. Future Improvements

Several improvements could make the analysis more rigorous.

## 19.1 Control for fuel load

Fuel mass affects lap time and normally decreases during a race.

Including estimated fuel load would help separate fuel effects from tyre-age effects.

## 19.2 Add sector-level analysis

Sector times could identify whether tyre-age effects are concentrated in:

* braking zones
* high-speed corners
* traction zones

## 19.3 Include weather

Weather variables could include:

* track temperature
* air temperature
* rainfall
* humidity

This would be particularly important for intermediate and wet tyres.

## 19.4 Include tyre stint information

Combining:

Compound
TyreLife
Stint
LapNumber
TrackStatus

could provide a more detailed view of tyre performance.

## 19.5 Improve the statistical model

A future version could use a multivariable regression or mixed-effects model incorporating:

Relative pace ~ TyreLife
              + Compound
              + Track
              + TrackStatus
              + Stint
              + Weather
              + other controls

This would provide a stronger framework for separating tyre-age effects from other factors.

---

# 20. Main Findings

The project produced several descriptive findings from the 2024 dataset:

1. Race finishing position varies substantially between drivers and is influenced by both driver and car/race factors.
2. Raw lap times are not directly comparable across different circuits.
3. Relative pace provides a more appropriate framework for comparing drivers within the same race context.
4. Tyre-age analysis shows different patterns across compounds.
5. HARD and MEDIUM compounds displayed positive associations between tyre age and relative pace in the weighted analysis.
6. SOFT showed little overall linear association in this model.
7. INTERMEDIATE showed a weak negative association, demonstrating the importance of changing track conditions.
8. The weighted analysis provides stronger descriptive evidence than the initial unweighted trend, but it does not establish causal tyre degradation.

---

# 21. Technical Skills Demonstrated

This project demonstrates practical experience with:

* Python
* pandas
* NumPy
* Matplotlib
* FastF1
* CSV data processing
* data cleaning
* exploratory data analysis
* statistical summaries
* linear regression
* weighted regression
* correlation analysis
* data visualization
* domain-specific data interpretation
* reproducible analysis pipelines

It also demonstrates an important data-science workflow:

Question
   ↓
Data collection
   ↓
Data cleaning
   ↓
Exploratory analysis
   ↓
Identify limitations
   ↓
Improve methodology
   ↓
Statistical analysis
   ↓
Interpretation
   ↓
Document limitations
   ↓
Propose future research

---

# 22. Project Conclusion

This project began as an analysis of Formula 1 race and lap data and developed into a progressively more controlled investigation of driver relative pace and tyre-age effects.

The main methodological lesson is that raw lap times alone are insufficient for meaningful cross-circuit comparison.

By normalizing lap performance within the same race and lap, excluding the driver's own observation from the comparison reference, and weighting tyre-age observations by the number of recorded laps, the analysis provides a more defensible exploratory investigation of tyre-age and relative-pace relationships.

The final results should be interpreted as **observational statistical associations**, rather than definitive measurements of physical tyre degradation.

Future work can extend the project toward multivariable modelling, telemetry, sector-level analysis, weather conditions, and computer-vision applications in motorsport.

---

## Project Outputs

### Raw data

data/raw/race_results_2024.csv
data/raw/race_laps_2024.csv

### Processed data

```text
data/processed/driver_finish_summary.csv
data/processed/driver_lap_pace_summary.csv
data/processed/driver_consistency_summary.csv
data/processed/tyre_usage_summary.csv
data/processed/driver_points_summary.csv
data/processed/driver_relative_pace_summary.csv
data/processed/race_driver_relative_pace.csv
data/processed/race_relative_pace_matrix.csv
data/processed/tyre_age_pace_summary.csv
data/processed/tyre_age_relative_pace_summary.csv
data/processed/controlled_tyre_age_relative_pace.csv
data/processed/tyre_degradation_trend.csv
data/processed/weighted_tyre_degradation_trend.csv
```

### Figures

outputs/figures/01_average_finish.png
outputs/figures/02_average_lap_time.png
outputs/figures/03_lap_time_consistency.png
outputs/figures/04_tyre_usage.png
outputs/figures/05_driver_points.png
outputs/figures/06_race_relative_pace.png
outputs/figures/07_race_by_race_relative_pace.png
outputs/figures/08_tyre_age_pace.png
outputs/figures/09_tyre_age_relative_pace.png
outputs/figures/10_controlled_tyre_age_relative_pace.png
outputs/figures/11_tyre_degradation_trend.png
outputs/figures/12_weighted_tyre_degradation_trend.png
