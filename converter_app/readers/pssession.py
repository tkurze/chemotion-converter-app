import json
import logging

from .base import Reader

logger = logging.getLogger(__name__)


class PsSessionReader(Reader):
    identifier = 'pssession_reader'
    priority = 10

    def check(self):
        if self.file.suffix != '.pssession':
            result = False
        else:
            result = True

        logger.debug('result=%s', result)
        return result

    def parse_json(self):
        try:
            return json.loads(self.file.content.strip(b'\xfe\xff'))
        except json.decoder.JSONDecodeError:
            return {}

    def get_tables(self):
        tables = []
        data = self.parse_json()

        measurements = data.get('measurements') or data.get('Measurements', [])
        for measurement in measurements:
            # each measurement is a table
            table = self.append_table(tables)

            # add the method field to the header
            method = measurement.get('method') or measurement.get('Method', '')
            table['header'] = method.splitlines()

            # add key value pairs from the method field to the metadata
            for line in table['header']:
                if not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=')
                        table['metadata'][key] = value
                    except ValueError:
                        pass

            # add measurement fields to the metadata
            title = measurement.get('title') or measurement.get('Title', '')
            table['metadata']['title'] = str(title)

            timestamp = measurement.get('timestamp') or measurement.get('TimeStamp', '')
            table['metadata']['timestamp'] = str(timestamp)

            deviceused = measurement.get('deviceused') or measurement.get('DeviceUsed', '')
            table['metadata']['deviceused'] = str(deviceused)

            deviceserial = measurement.get('deviceserial') or measurement.get('DeviceSerial', '')
            table['metadata']['deviceserial'] = str(deviceserial)

            dataset = measurement.get('dataset') or measurement.get('DataSet', {})
            type_value = dataset.get('type') or dataset.get('Type', '')
            table['metadata']['type'] = str(type_value)

            # exctract the columns
            columns = []
            dataset = measurement.get('dataset') or measurement.get('DataSet', {})
            values = dataset.get('values') or dataset.get('Values', [])
            for idx, values in enumerate(values):
                # each array is a column
                column_name = values.get('description') or values.get('Description', '')

                # add the column name to the metadata
                table['metadata']['column_{:02d}'.format(idx)] = column_name

                # add the column name to list of columns
                table['columns'].append({
                    'key': str(idx),
                    'name': 'Column #{} ({})'.format(idx, column_name)
                })

                # append the "datavalues" to list data list of lists
                datavalues_list = values.get('datavalues') or values.get('DataValues', [])
                columns.append([datavalues.get('v') or datavalues.get('V', None) for datavalues in datavalues_list])


            # transpose data list of lists
            table['rows'] = list(map(list, zip(*columns)))

            # add number of rows and columns to metadata
            table['metadata']['rows'] = str(len(table['rows']))
            table['metadata']['columns'] = str(len(table['columns']))

        return tables

    def get_metadata(self):
        metadata = super().get_metadata()
        data = self.parse_json()
        metadata['type'] = data.get('type') or data.get('Type', '')
        return metadata

