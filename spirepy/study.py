import tarfile
import os.path as path
import os
import urllib

import polars as pl

from spirepy.logger import logger
from spirepy.data import genome_metadata


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

    def __init__(self, name: str):
        self.name = name
        self._metadata = None
        self._samples = None
        self._mags = None

    @property
    def metadata(self):
        if self._metadata is None:
            study_meta = pl.read_csv(
                f"https://spire.embl.de/api/study/{self.name}?format=tsv",
                separator="\t",
            )
            self._metadata = study_meta
        return self._metadata

    @property
    def samples(self):
        from spirepy.sample import Sample

        if self._samples is None:
            sample_list = []
            for s in self.metadata["sample_id"].to_list():
                sample = Sample(s, self)
                sample_list.append(sample)
            self._samples = sample_list
        return self._samples

    @property
    def mags(self):
        if self._mags is None:
            genomes = genome_metadata()
            self._mags = genomes.filter(
                genomes["derived_from_sample"].is_in(
                    self.metadata["sample_id"].to_list()
                )
            )
        return self._mags

    def download_mags(self, output: str):
        os.makedirs(output, exist_ok=True)
        urllib.request.urlretrieve(
            f"https://swifter.embl.de/~fullam/spire/compiled/{self.name}_spire_v1_MAGs.tar",
            path.join(output, f"{self.name}_mags.tar"),
        )
        tar = tarfile.open(path.join(output, f"{self.name}_mags.tar"))
        tar.extractall(path.join(output, "mags"))
        tar.close
