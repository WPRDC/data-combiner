import io
import csv

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


def get_csv_data(file_path, row_limit=0):
    n = 1
    data = []
    with open(file_path) as f:
        reader = csv.reader(f)
        for row in reader:
            data.append([str(c) for c in row])
            if n == row_limit + 1:  # the extra 1 is for the header
                break
            n += 1

    return data