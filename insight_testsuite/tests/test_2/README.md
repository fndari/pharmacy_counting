# test_2

Basic test for data quality. The input file contains malformed output. 

- Line 1: Contains an empty value for `prescriber_first_name`. Since this is not required by the challenge, this line is not rejected by the default data validator (`is_valid_for_challenge()`), and is included in the output in the existing version of the code
- Line 2: Contains an erroneous number of values
    + The Python `csv.reader` function processes files line-by-line, so it's possible to have single lines with the wrong number of fields
    + This line is skipped from processing, and is not included in the output
- Line 5: the value of `id` cannot be converted to the expected value (assumed to be an integer)
    + This line is skipped from processing, and is not included in the output