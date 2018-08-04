import pytest

from pharmacy_counting.data import *
from pharmacy_counting.config import CURRENCY_TYPE, ID_TYPE
from pharmacy_counting.util import DefaultDictKeyAsArg


def test_prescription_valid_input():
    input_row = ('123', 'Last', 'First', 'DRUGNAME', '1345')

    p = Prescription.from_tuple(input_row)

    # check that non-string types are converted correctly
    assert p.id == ID_TYPE(input_row[0])
    assert p.drug_cost == CURRENCY_TYPE(input_row[4])


def test_prescription_invalid_input():
    """Checks that data quality precautions work as expected"""

    non_convertible_id = ('non a number', 'Last', 'First', 'DRUGNAME', '1234')

    with pytest.raises(ValueError):
        p = Prescription.from_tuple(non_convertible_id)

    wrong_number = ('123', 'Last', 'First', 'DRUGNAME')

    with pytest.raises(ValueError):
        p = Prescription.from_tuple(wrong_number)


def test_normalize_case():

    assert normalize_case('some name')\
        == normalize_case('Some Name')\
        == normalize_case('SOME NAME')


def test_drugsummary_counting():
    pres = [
        Prescription.from_tuple(vals) for vals in [
            (1, 'Smith', 'John', 'DRUG1', 100),
            (2, 'Smith', 'John', 'DruG1', 200),
            (3, 'Doe', 'Jane', 'Drug1', 300),
            (4, 'Doe', 'Jane', 'Another drug', 400),
        ]
    ]

    drugs = DefaultDictKeyAsArg(DrugSummary)
    for pre in pres:
        drugs[pre.drug_name].add_prescription(pre)
        print(pre)

    summary_drug1 = drugs[normalize_case('drug1')]
    assert summary_drug1.total_cost == 600
    assert summary_drug1.num_prescriber == 2

    summary_drug2 = drugs[normalize_case('Another drug')]
    assert summary_drug2.total_cost == 400
    assert summary_drug2.num_prescriber == 1

