import csv

from pharmacy_counting.config import (PATH_INPUT, INPUT_LINES_MAX, input_format_opts,
                                      LOG_SKIPPED,
                                      PATH_OUTPUT, output_format_opts, fields_output
                                      )

from pharmacy_counting.data import Prescription, DrugSummary, is_valid_for_challenge as is_valid
from pharmacy_counting.util import DefaultDictKeyAsArg


# from memory_profiler import profile


# @profile
def main():
    table_drugs = DefaultDictKeyAsArg(DrugSummary)

    with PATH_INPUT.open('r') as f:
        reader = csv.reader(f, **input_format_opts)

        for line_idx, line in enumerate(reader):
            if line_idx == 0:  # skip output header (this assumes it being on the first line)
                continue
            if line_idx > INPUT_LINES_MAX:
                break

            try:
                prescription = Prescription.from_tuple(line)
            except ValueError as e:
                LOG_SKIPPED(line_idx, e)
                continue
            else:
                if is_valid(prescription):
                    table_drugs[prescription.drug_name].add_prescription(prescription)
                else:
                    LOG_SKIPPED(line_idx, f'prescription does not pass validation requirements.\n\t{prescription}')

    drugs = list(table_drugs.values())
    # sort by name first
    drugs.sort(key=lambda x: x.name)
    # this two-pass sorts achieves the desired result (sort by cost, then if tie sort by name)
    # because the default sorting algorithm preserves any ordering existing in the input
    drugs.sort(key=lambda x: x.total_cost, reverse=True)

    with PATH_OUTPUT.open('w') as f:
        writer = csv.writer(f, **output_format_opts)
        writer.writerow(fields_output)  # write output header
        writer.writerows([drug.to_tuple() for drug in drugs])


if __name__ == '__main__':
    main()
