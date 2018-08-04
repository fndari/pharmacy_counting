# The challenge at a glance
+ The fundamental operation required by the challenge is to extract aggregate information from a `prescription` table, using its `drug_name` field
+ If I were to implement it without the challenge restrictions, using e.g. pandas, this would mean a `groupby` operation on the `drug_name` column, followed by an `aggregate` operation, using `sum` on `drug_cost` and `nunique` on `prescriber_id`
+ Another Python solution, similar to the previous one but without using pandas, would be to read the CSV file to a SQLite database table, and then issuing a `GROUP BY` query using the `SUM` and `COUNT DISTINCT` aggregation functions.

# Design

## General Architecture
- I used a row-based paradigm, supported by classes (`Prescription` and `DrugSummary`) to represent the fundamental domain data units. The main advantages of this approach:
    - Easy to read, and naturally domain-aligned: natural correspondence input line <-> table record <-> Python object
    - Easy to write: CSV files in Python are read and written line-by-line, and record instances can naturally be serialized to/from `tuple`s
    - Numpy and pandas are primarily column-oriented, among other reasons, for performance. Implementing a column-based framework for the purpose of the challenge did not seem to be a good idea, especially for the  purpose of this challenge (since no explicit performance targets were given), but also in general (reinventing the wheel, unless of course there were particular requirements to do so)
- Since the problem presents a natural high degree of coupling between the data (the values in the record fields) and operations on the data, classes were used instead of a non-OO approach using plain `dict` instances and free functions


## `Prescription` class
+ Its instances represent records in the input table
+ I exploited the fact that, once converted, its data attributes are immutable for its implementation as a `namedtuple` from the `collections` module in the Python standard library (plus additional functionality)

## `DrugSummary` class
+ Its instances represent records in the output table
+ A `namedtuple` could not be used in this case, because the data attributes are mutated after instantiation. I used the `__slots__` class attribute to freeze the data attributes, for the purpose of explicitly enforcing constraints on the API, and helping reducing memory usage for each instance (at least 15%, from a cursory A/B comparison using the Python module `memory_profiler`)

## Table-like data structure
- The `table_drugs` data structure is implemented as a `defaultdict` variant with a `DrugSummary` class as its default factory, so that indexing (`[]`/`__getitem__`) fetches or creates the corresponding record (semantically similar to an `UPSERT` operation in database terms). The automatic insertion of `drug_name` in the `DrugSummary` instances keeps the `keys` of `table_drugs` in sync with its `values`, establishing a rough conceptual correspondence `keys` -> table index, `values` -> table rows/records

## Data Quality
- I implemented basic functionality to ensure proper treatment of invalid data
- In absence of an example of a real-world "dirty" dataset, only basic assumptions can be made about how defensive the conditions should be. Considering only the specific task required in the challenge, it seems sufficiently robust to inexact data, e.g. if there are transactions where the drug name is not given, these will automatically be grouped together; similarly with prescribers
    + On the other hand, the aggregated results will be not correct if the same drug is recorded with different names. In database terms, this could be addressed by using normalized tables (e.g. a `drugs` table and a `prescribers` table) and encoding the relation between them using unique identifiers (primary keys), e.g. storing `drug_id` in the `prescriptions` dataset instead of `drug_name`
- Without explicit requirements for invalid data, my approach is to notify the location and the nature of the error, and skip the corresponding record. In the current version, the notification is printed to stdout. This can be modified using a different `LOG_SKIPPED` function
- The "conversion" (converting the raw types given by the input format reader to domain-appropriate ones) and the "validation" (deciding if a record should be processed in the analysis) steps are conceptually separate (although there is some amount of overlap), so I keep them separate in the code as well. The criteria for validation belong logically both to the input record and the analysis being performed, so they are implemented as an independent function rather then as a method of the `Prescription` class
- A failed deserialization or conversion is propagated to the client as a `ValueError` exception
- Among the possible erroneous data types considered:
    + Wrong number of values, potentially caused by missing separators in the input file
    + Non-numeric input values when numeric values are expected
    + Null values (as exemplified in the `is_valid_stricter()` validator)

## Source layout
- I decided to separate different parts of the project as a Python package `pharmacy_counting` comprising a few modules:
    + `util` contains all common utilities
    + `config` contains common settings, that can be accessed and imported by other modules
    + `data` contains the model classes, as well as the data-specific functions
    + `run` contains the actual operations in the analysis
- NOTA BENE: this package structure requires an additional step when invoking the `run` module, i.e. adding the `src/` directory to the Pythonpath (this is done in the `run.sh` script, by adding that directory to the `PYTHONPATH` environment variable)
    + This is not needed when installing the package using e.g. `setup.py`

# Miscellaneous Remarks

## Currency
- When representing currency, using floating point numeric types (`float` in Python) is discouraged. Having never dealt with money in a production environment, my first choice would be to research best practices and/or libraries to deal with currency, at the level required for the application. Under the challenge restrictions, I chose to use the `Decimal` class from the `decimal` module in the Python standard library for fixed-point computation
- A lower-level alternative would be to represent the smallest currency unit (in case of USD, 0.01 USD) as `int`s, and then multiply or divide (in case of USD, by 100) opportunely. For this particular application it would be OK (since only sums are involved), but unexpected results may occur if dealing with multiplication or division. Again, the optimal implementation depends by the precision needed by the application
- There can be a potential inconsistency when the result of a cost computation is a round number. In the default test provided, the costs are expressed in whole dollars (i.e. 200 USD shows up as `200`), but when computing a larger amount of prescriptions, the probability of it having a whole dollar result is low (naively, 1/100 = 1%). This can create ambiguity and/or inconsistency when e.g. displaying `200` instead of `200.00`. If the application requires consistency in this case, a variant of `serialize_currency` can be used to explicitly write the amount in cents even for whole dollar amounts

## Running on the large dataset (24M rows)
- I successfully ran the analysis on the large dataset provided, but because of the large size I did not include the dataset in the directories provided
- Without careful profiling and optimization, the performance seems acceptable: the runtime (single-threaded) is about 2--3 minutes, and the memory consumption of about 2--3 GB
- There are several names (both `prescriber_first_name` and `prescriber_last_name`) that contain single quotes (`'`) characters. This might require extra attention/quoting. Most CSV dialects or variants use double quotes for quoting, so they should not pose a problem for the purpose of the challenge. If the original dataset is not 
- The `id` field of the input file (`prescription` table) is not unique to each line. It seems to be an integer, compatible with a timestamp (UNIX epoch), thus readable as a `datetime` object, however I refused the temptation to guess and did not include this information in the code (it was in any case not needed)


# Additional unit tests
In addition to the ones in the `insight_testsuite`, additional unit tests are available in the `tests` subdirectory. The tests require `pytest` to run (`pip install pytest; pytest -v name_of_test_module.py`).

# Outlook

In other words, what would I do differently?
- Of course, the most important input to decide on any further extension or modification to the code are the requirements of further analysis
- An extension of the class-based approach used could lead to an ORM-like implementation, where:
    - all the domain logic is concentrated in `Model` subclasses
    - Records are represented as model class instances, stored and managed transparently from the client, and are accessed in the client from class instances with e.g. a `Model.get_or_create(primary_key)` class method
    The advantage is that the API would be a bit cleaner, and would allow e.g. to optimize or rearrange the "backend" (the layout of the database table equivalent, at the moment, a subclass of a Python `dict`) independently of the analysis code. However, this requires careful consideration, both to research the best architecture to implement it, and most importantly to decide whether the added complexity would actually be worth the flexibility: for this reason, I did not progress further with this idea.
- One could argue that the separation between the `data` and `run` modules, or, more conceptually, areas, is somewhat porous, and should be researched more carefully
    + If the workflow of potential future analyses is similar, the I/O operations could be factored out, and possibly moved to a `Tablelike` interface in the `Model` classes
- To improve performance, the necessary step is to profile the code carefully, and only then tackle clear performance hotspots
    + In general, were the profiling results to show that this is a CPU-bound operation, one approach could be to use parallel processing using Python multiprocessing to exploit all available processors on a multicore machine
    + This is an "embarassingly parallel" algorithm, since there is no dependency in the input data, but the necessity of merging partial aggregation operation could introduce a potentially significant overhead
    + From the point of view of the code, this would require splitting the input lines between the desired worker units, each producing a `table_drugs` instance, and then implement an additional function to merge them to a single table


# Appendix

## Results of running with the large (24M rows) dataset

```txt
> /usr/bin/time -v ./run.sh
        Command being timed: "./run.sh"
        User time (seconds): 153.61
        System time (seconds): 1.74
        Percent of CPU this job got: 99%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 2:35.38
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 2468256
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 13
        Minor (reclaiming a frame) page faults: 709591
        Voluntary context switches: 147
        Involuntary context switches: 656
        Swaps: 0
        File system inputs: 2268280
        File system outputs: 152
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0
```