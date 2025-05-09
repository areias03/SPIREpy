import os
import os.path as path
import urllib.request

import polars as pl
import pandas as pd

from spirepy.logger import logger
from spirepy.data import cluster_metadata
from spirepy.study import Study


class Sample:
    """
    A sample from SPIRE.

    This class represents a sample from the SPIRE database. It is designed to
    provide all the properties and methods to allow work with samples and
    provide tools for automation and scalability.

    Attributes:

    id: str
        Internal ID for the sample.
    study: Study
        Study ID to which the sample belongs to.
    """

    def __init__(self, id: str, study: Study = None):
        """
        Creates a new sample object.
        """
        self.id = id
        self.study = study
        self._metadata = None
        self._manifest = None
        self._mags = None
        self._eggnog_data = None
        self._amr_annotations = None

    def __str__(self):
        return f"Sample id: {self.id} \tStudy: {[self.study.name if type(self.study) is Study else None]}"

    def __repr__(self):
        return self.__str__()

    @property
    def metadata(self):
        if self._metadata is None:
            sample_meta = pl.read_csv(
                f"https://spire.embl.de/api/sample/{self.id}?format=tsv", separator="\t"
            )
            self._metadata = sample_meta
        return self._metadata

    @property
    def mags(self):
        if self._mags is None:
            cluster_meta = cluster_metadata()
            clusters = self.metadata.filter(self.metadata["spire_cluster"] != "null")
            mags = cluster_meta.filter(
                cluster_meta["spire_cluster"].is_in(clusters["spire_cluster"])
            )
            mags = mags.join(clusters, on="spire_cluster")
            mags = mags.select(
                pl.col("spire_id"),
                pl.col("sample_id"),
                pl.all().exclude(["spire_id", "sample_id"]),
            )
            self._mags = mags
        return self._mags

    @property
    def eggnog_data(self):
        if self._eggnog_data is None:
            egg = pd.read_csv(
                f"https://spire.embl.de/download_eggnog/{self.id}",
                sep="\t",
                skiprows=4,
                skipfooter=3,
                compression="gzip",
                engine="python",
            )
            eggnog_data = pl.from_pandas(egg)
            self._eggnog_data = eggnog_data
        return self._eggnog_data

    @property
    def amr_annotations(self):
        if self._amr_annotations is None:
            amr = self.get_amr_annotations()
            self._amr_annotations = amr
        return self._amr_annotations

    def get_amr_annotations(self, mode: str = "deeparg"):
        mode_match = {
            "deeparg": f"https://spire.embl.de/download_deeparg/{self.id}",
            "megares": f"https://spire.embl.de/download_abricate_megares/{self.id}",
            "vfdb": f"https://spire.embl.de/download_abricate_vfdb/{self.id}",
        }
        if mode not in mode_match.keys():
            logger.error(
                "Invalid option, please choose one of the following: deeparg, megares, vfdb"
            )
            return None
        url = [val for key, val in mode_match.items() if key == mode][0]
        amr = pl.read_csv(url, separator="\t")
        return amr

    def download_mags(self, out_folder):
        os.makedirs(out_folder, exist_ok=True)
        for mag in self.mags["spire_id"].to_list():
            urllib.request.urlretrieve(
                f"https://spire.embl.de/download_file/{mag}",
                path.join(out_folder, f"{mag}.fa.gz"),
            )
