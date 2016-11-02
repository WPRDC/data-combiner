import io
import csv
from collections import OrderedDict

from combiner.models import InputDocument, CKANField, CKANResource, CKANInstance


def parse_csv(file, encoding='utf-8'):
    _file = io.StringIO(file.read().decode(encoding))
    try:
        dr = csv.DictReader(_file)
        rows = 0
        for row in dr:
            rows += 1

        newdoc = InputDocument(file=file,
                               headings=",".join(dr.fieldnames),
                               rows=rows)
        newdoc.save()
        return newdoc.id

    except csv.Error:
        return False


def get_csv_data(file_path, row_limit=-1):
    n = 1
    data = []
    fields = []
    with open(file_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            ordered_row = OrderedDict()

            for k in reader.fieldnames:
                ordered_row[k] = row[k]

            data.append(ordered_row)

            if n == 1:
                fields = reader.fieldnames

            if n == row_limit + 1:  # the extra 1 is for the header
                break
            n += 1

    return data, fields
