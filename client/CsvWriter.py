import csv


class CsvWriter:
    def __init__(self, f, dialect=csv.excel, **kwargs):
        self.writer = csv.writer(f, dialect=dialect, **kwargs)

    def write_row(self, row):
        self.writer.writerow(row)

    def write_rows(self, rows):
        for row in rows:
            self.write_row(row)