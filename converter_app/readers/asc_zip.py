import logging
import os
import tempfile
from zipfile import ZipFile
from converter_app.readers.helper.base import Reader
from converter_app.readers.helper.reader import Readers
from converter_app.readers.helper.asc_helper import AscHelper

logger = logging.getLogger(__name__)


class AscZipReader(Reader):
    """
    Reader unzips a zip archive and reads single asc files.  It extends converter_app.readers.helper.base.Reader
    """
    identifier = 'asc_zip_reader'
    priority = 10

    def __init__(self, file):
        super().__init__(file)
        self.filedata = {}

    # two or more chars in row

    def check(self):
        """
        :return: True if it fits
        """
        result = False

        if self.file.suffix.lower() == '.zip' and self.file.mime_type == 'application/zip':
            with ZipFile(self.file.fp, 'r') as zip_obj:
                list_of_file_names = zip_obj.namelist()
                if any(fileName.lower().endswith('.asc') for fileName in list_of_file_names):
                    with tempfile.TemporaryDirectory() as td:
                        zipdir = os.path.join(td, os.path.basename(self.file.name))
                        os.makedirs(zipdir)
                        result = True
                        # Iterate over the file names
                        for file_name in list_of_file_names:
                            # Check filename endswith csv
                            if file_name.lower().endswith('.asc'):
                                # Extract a single file from zip
                                path_file_name = zip_obj.extract(file_name, zipdir)
                                with open(path_file_name, mode="r", encoding="latin_1") as f:
                                    self.filedata[file_name] = f.readlines()

        return result

    ###############################################################################
    # formatResultsElab
    ###############################################################################
    def format_results_chemotion(self, results):
        """
        Formats results (list of dictionaries) generated by the ALV parser for DLS
        data to fit metadata for eLabFTW.
        Renames metadata, ensures formats are correct.
        """
        metadata = {}
        data = {}

        # sample ID = Samplename
        metadata["Samplename"] = results[0]["Samplename"]
        # DLS device = Device Info --> options
        metadata["Device Info"] = results[0]["Device Info"].split("/")[0]
        # if results[0]['SampleMemo']:

        # solvent = nothing, needs to be filled in manually for dls (?)
        # sample volume [ml] = nothing, needs to be filled in manually for dls (?)
        metadata["wavelength [nm]"] = str(results[0]["Wavelength [nm]"])
        # measurement starting time --> earlierst "Date" in all the dates (don't hard code)
        time_obj = AscHelper.get_startdate(results)
        metadata["measurement starting time"] = str(time_obj['startdate_object'])

        data["duration [s]"] = time_obj['time_line']

        # relative time point [s] --> TODO ?
        # refractive index --> refractive index from LIST
        data["refractive index"] = AscHelper.list_values("Refractive Index", results)

        # temperature [K] --> Temperature [K] from LIST
        data["temperature [K]"] = AscHelper.list_values("Temperature [K]", results)

        # viscosity [mPas] --> Viscosity [cp] from LIST
        data["viscosity [mPas]"] = AscHelper.list_values("Viscosity [cp]", results)

        # detection angle [°] --> Angle [°] from LIST TODO decide on unit
        data["detection angle [degrees]"] = AscHelper.list_values("Angle [°]", results)

        # average diffusion coefficient [micron^2/s] --> Diffusion Coefficient 2. order fit [µm²/s] from LIST
        data["average diffusion coefficient [micron^2/s]"] = AscHelper.list_values(
            "Diffusion Coefficient 2. order fit [µm²/s]", results)

        # second cumulant (expansion parameter) --> Expansion Parameter µ2 from LIST
        data["second cumulant (expansion parameter)"] = AscHelper.list_values("Expansion Parameter µ2", results)

        # hydrodynamic radius [nm] --> Hydrodynamic Radius 2. order fit [nm]
        data["hydrodynamic radius [nm]"] = AscHelper.list_values("Hydrodynamic Radius 2. order fit [nm]", results)

        # average diffusion coefficient [micron^2/s] --> Diffusion Coefficient 2. order fit [µm²/s] from LIST
        data["average diffusion coefficient [micron^2/s]"] = AscHelper.list_values(
            "Diffusion Coefficient 2. order fit [µm²/s]", results)

        # second cumulant (expansion parameter) --> Expansion Parameter µ2 from LIST
        data["second cumulant (expansion parameter)"] = AscHelper.list_values("Expansion Parameter µ2", results)

        # hydrodynamic radius [nm] --> Hydrodynamic Radius 2. order fit [nm]
        data["hydrodynamic radius [nm]"] = AscHelper.list_values("Hydrodynamic Radius 2. order fit [nm]", results)

        for (key, val) in data.items():
            metadata[key] = AscHelper.str_vals(val)

        # duration [s] = Duration [s]
        metadata["duration [s]"] = str(results[0]["Duration [s]"])

        # first correlation delay [ms] TODO ?

        return {
            'data': data,
            'metadata': metadata
        }

    def prepare_tables(self):
        tables = []
        table = self.append_table(tables)
        all_results = []  # will contain a dict for each file parsed
        helper = AscHelper()
        for (file_name, file_content) in self.filedata.items():
            results = helper.parsefile_alv(file_name, file_content)
            all_results.append(results)

        all_results.sort(key=lambda x: x["Datetime"])
        formated_results = self.format_results_chemotion(all_results)
        table['metadata'] = formated_results['metadata']
        col_names = list(formated_results['data'].keys())
        table['columns'] = [{
            'key': str(idx),
            'name': f'{value}'
        } for idx, value in enumerate(col_names)]
        for idx in range(len(formated_results['data'][col_names[0]])):
            table['rows'].append([formated_results['data'][name][idx] for name in col_names])

        return tables


Readers.instance().register(AscZipReader)
