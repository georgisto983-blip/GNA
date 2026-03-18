# GNA
## Workflow1
Exaple imput for calculating half-life by using data from single plunger distance:
```
{
    "work_mode": "1",
    "plunger_distance": "13 0.5", 
    "beta": "0.008 0.0001",
    "area_shifted": "7600 300",
    "area_unshifted": "4300 90"
}
```
## Workflow2
Example imput for calculating half-life by using data from multiple distances:
```
{
    "work_mode": "2",
    "beta": [0.008, 0.0001],

    "plunger_distance": [
        [13, 0.5],
        [14, 0.5]
    ],
    "area_shifted": [
        [6634, 435],
        [3946, 185]
    ],
    "area_unshifted": [
        [5175, 497],
        [3491, 217]
    ]
}
```
