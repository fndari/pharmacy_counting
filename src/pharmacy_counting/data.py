import collections
from .config import ID_TYPE, CURRENCY_TYPE, fields_input


def normalize_case(val):
    return str(val).upper()


PrescriptionBase = collections.namedtuple('PrescriptionBase', fields_input)


class Prescription(PrescriptionBase):

    converters = {
        'id': ID_TYPE,
        'prescriber_last_name': normalize_case,
        'prescriber_first_name': normalize_case,
        'drug_name': normalize_case,
        'drug_cost': CURRENCY_TYPE,
    }

    @classmethod
    def from_tuple(cls, values, field_names=fields_input):
        """
        Deserialize from the format given by the input file reader.
        """

        converted = []
        try:
            assert len(values) == len(field_names), 'values provided do not match number of expected fields'
        except AssertionError as e:
            raise ValueError('Missing fields: {}'.format(e))
        else:
            for name, value in zip(field_names, values):
                converter = cls.converters[name]
                try:
                    val_converted = converter(value)
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        'Was not possible to convert "{value}" using "{converter}" for field "{name}"'
                        .format(**locals())
                    )
                else:
                    converted.append(val_converted)

        return cls(*converted)


def get_prescriber_id(prescription):
    return ','.join([prescription.prescriber_last_name, prescription.prescriber_first_name])


def is_valid_for_challenge(prescription):
    """
    Check if `prescription` is valid for processing, according to criteria explicitly required for the challenge.
    """
    return all([
        prescription.drug_name != '',
    ])


def is_valid_stricter(prescription):
    """
    Check if `prescription` is valid for processing, using some basic criteria of data sanity,
    although not explicitly required by the challenge.
    """
    return all([
        prescription.prescriber_last_name != '',
        prescription.prescriber_first_name != '',
        prescription.drug_name != '',
        prescription.drug_cost >= CURRENCY_TYPE(0.00),
    ])


def serialize_currency(amount):
    # return f'{amount:.2f}'
    return str(amount)


# factor out common interface to base class, in case variants of DrugSummary are needed
# (for both additional functionality and/or performance)
class DrugSummaryBase:

    def __repr__(self):
        clsname = type(self).__name__
        return (
            '{clsname}({self.name}: num_prescriber={self.num_prescriber}, total_cost={self.total_cost})'.format(**locals())
        )

    def add_prescription(self, prescription):
        raise NotImplementedError

    def to_tuple(self):
        """
        Serialize to the format expected by the output writer.
        """
        return self.name, self.num_prescriber, serialize_currency(self.total_cost)


class DrugSummary(DrugSummaryBase):

    __slots__ = ('name', 'total_cost', '_prescribers')

    def __init__(self, name=''):
        self.name = name

        # total_cost can be used directly, without accumulating intermediate drug_cost values
        # CURRENCY_TYPE() should initialize to 0 by default, but explicit is better than implicit
        self.total_cost = CURRENCY_TYPE(0)

        # on the contrary, it's necessary to accumulate a per-drug account of prescribers
        # since we're only interested in the unique prescribers, a set is used
        self._prescribers = set()

    def add_prescription(self, prescription):
        self.total_cost += prescription.drug_cost

        prescriber_id = get_prescriber_id(prescription)
        self._prescribers.add(prescriber_id)

    @property
    def num_prescriber(self):
        return len(self._prescribers)
