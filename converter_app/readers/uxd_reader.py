import logging

from converter_app.models import File
from converter_app.readers.helper.reader import Readers
from converter_app.readers.helper.base import Reader

logger = logging.getLogger(__name__)


class UXDReader(Reader):
    """
    Reader for UDX files. Files from: Powder Diffraction -  Diffrac Plus

    Test File: test_files/data_files/Powder Diffraction/Diffrac Plus/XCH-UXD/PD-01-02(2).UXD
    """

    identifier = 'uxd_reader'
    priority = 10



    def __init__(self, file: File):
        super().__init__(file)
        self._file_extensions = ['.uxd']
        self._table = None
        self._version = 2

    def check(self):
        return self.file.suffix.lower() in self._file_extensions

    def _read_data(self, line: str):
        if self._version == 2:
            try:
                for value in [self.as_number(x.strip()) for x in line.split(' ') if x != '']:
                    self._table['rows'].append([value])
            except ValueError:
                pass
        elif self._version == 3:
            try:
                value = [self.as_number(x.strip()) for x in line.split('\t')]
                self._table['rows'].append([value[0], value[1]])
            except ValueError:
                pass

    def prepare_tables(self):
        tables = []
        tables = []
        # xml_str = re.sub(r'\sxmlns\s*([:=])', r' xmlns_removed\g<1>', self.file.string)
        self._table = self.append_table(tables)
        data_rows = []
        for row in self.file.fp.readlines():
            line = row.decode(self.file.encoding).rstrip()

            if len(line) > 1 and (line[0] == '_' or line[0] == ';'):
                self._table['header'].append(line)
                if line[0] == '_' and line[1] != '+' and '=' in line:
                    data = line.split('=')
                    key = data[0].strip()[1:]
                    value = data[1].strip().replace('\n', '')
                    self._table.add_metadata(key, value)
            else:
                data_rows.append(line)
        try:
            self._version = int(self._table['metadata'].get('FILEVERSION'))
        except ValueError:
            self._version = 0

        for row in data_rows:
            self._read_data(row)

        return tables


Readers.instance().register(UXDReader)

