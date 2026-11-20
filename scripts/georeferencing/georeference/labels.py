"""Parse only a visually established unit convention; never guess ambiguous labels."""
from decimal import Decimal
import re


def parse_grid_label(text, printed_unit):
    text=text.strip().replace('−','-')
    if printed_unit in ('kilometre','hectometre'):
        if not re.fullmatch(r'[+-]?\d+(?:[.,]\d+)?',text):raise ValueError('Ambiguous '+printed_unit+' label')
        return float(Decimal(text.replace(',','.'))*(1000 if printed_unit=='kilometre' else 100))
    if printed_unit=='metre':
        if re.fullmatch(r'[+-]?\d+',text):return int(text)
        if re.fullmatch(r'[+-]?\d{1,3}(?:\.\d{3})+',text):return int(text.replace('.',''))
        raise ValueError('Metre label has ambiguous separators')
    raise ValueError('Printed units must be reviewed explicitly')
