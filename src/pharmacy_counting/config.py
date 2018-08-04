from .util import log_skipped_stdout
from pathlib import Path
from decimal import Decimal
import math

LOG_SKIPPED = log_skipped_stdout

PATH_BASE = Path('.')

# semantically equivalent of a typedef in a statically typed language
CURRENCY_TYPE = Decimal
ID_TYPE = int

PATH_INPUT = PATH_BASE / 'input/itcont.txt'
fields_input = ['id', 'prescriber_last_name', 'prescriber_first_name', 'drug_name', 'drug_cost']
input_format_opts = {'delimiter': ','}
_UNLIMITED = math.inf
INPUT_LINES_MAX = _UNLIMITED

PATH_OUTPUT = PATH_BASE / 'output/top_cost_drug.txt'
# PATH_OUTPUT = Path('/home/ludo/Dropbox/jobhunt/coding/insight-2018-08-04/my-repo/output-big.txt')
fields_output = ['drug_name', 'num_prescriber', 'total_cost']
output_format_opts = {'delimiter': ','}
