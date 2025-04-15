import io
import os

import pandas as pd
import requests

from spirepy import Sample
from spirepy.logger import logger


class Study:
    """
    A study from SPIRE.

    This class represents a study from the SPIRE database. It automatically
    fetches metadata and automates the initialization of samples to further use
    to obtain its genomic, geographical or other types of data provided by it.

    Attributes:

    name: str
        Internal ID for the study.
    out_folder: str
        Folder to which the files from the study should be downloaded to.
    """

    def __init__(self, name: str, out_folder: str):
        self.name = name
        self.folder = out_folder
        self._metadata = None
        self._samples = None
        self._manifest = None

        os.makedirs(self.folder, exist_ok=True)

    @property
    def metadata(self):
        if self._metadata is None:
            logger.warning("No study metadata, downloading from SPIRE...\n")
            url = requests.get(
                f"https://spire.embl.de/api/study/{self.name}?format=tsv"
            ).text
            study_meta = pd.read_csv(io.StringIO(url), sep="\t")
            self._metadata = study_meta
        return self._metadata

    @property
    def samples(self):
        if self._samples is None:
            sample_list = []
            for s in self.metadata.sample_id.tolist():
                sample = Sample(s, self)
                sample_list.append(sample)
            self._samples = sample_list
        return self._samples

    @property
    def manifest(self):
        if self._manifest is None:
            print("No manifest")

        return self._manifest

    def process_all_samples(self):
        for sample in self.samples:
            logger.info(f"Processing sample {sample.id}")
