import os
import io
import subprocess

import requests
import urllib.request

import pandas as pd
import os.path as path

from .study import Study
from spirepy.data import genome_metadata
from spirepy.logger import logger
from spirepy.util import clean_emapper_data


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

    def __init__(self, id: str, study: Study):
        """
        Creates a new sample object.
        """
        self.id = id
        self.study = study
        self.out_folder = path.join(study.folder, self.id)
        self._eggnog_data = None
        self._mags = None
        self._reconstructions = None
        self._metadata = None
        self._manifest = None

        os.makedirs(self.out_folder, exist_ok=True)

    def __str__(self):
        return f"Sample id: {self.id} \tStudy: {self.study.name}"

    def __repr__(self):
        return self.__str__()

    @property
    def eggnog_data(self):
        if self._eggnog_data is None:
            urllib.request.urlretrieve(
                f"https://spire.embl.de/download_eggnog/{self.id}",
                path.join(self.out_folder, "emapper_annotations.gz"),
            )
            eggnog_data = clean_emapper_data(
                path.join(self.out_folder, "emapper_annotations.gz")
            )
            eggnog_data.to_csv(
                path.join(self.out_folder, "emapper_annotations.tsv", sep="\t")
            )
            self._eggnog_data = eggnog_data
        return self._eggnog_data

    @property
    def mags(self, download: bool = False):
        if self._mags is None:
            spire_meta = genome_metadata()
            masked = spire_meta.loc[spire_meta["derived_from_sample"] == self.id]
            self._mags = masked
        if download:
            self.download_mags()
        return self._mags

    @property
    def reconstructions(self):
        if self._reconstructions is None:
            list_reconstructions = []
            logger.warning("Starting reconstruction process...")
            for mag in self.mags.genome_id.tolist():
                recon = self.reconstruct(mag)
                list_reconstructions.append(recon)
                print(f"Finished reconstruction for {mag}")
        self._reconstructions = list_reconstructions
        return self._reconstructions

    @property
    def metadata(self):
        if self._metadata is None:
            logger.warning("No sample metadata, downloading from SPIRE...\n")
            url = requests.get(
                f"https://spire.embl.de/api/sample/{self.id}?format=tsv"
            ).text
            sample_meta = pd.read_csv(io.StringIO(url), sep="\t")
            self._metadata = sample_meta
        return self._metadata

    @property
    def manifest(self):
        if self._manifest is None:
            self._manifest = self.generate_manifest()
        return self._manifest

    def download_mags(self):
        mag_folder = path.join(self.out_folder, "mags/")
        os.makedirs(mag_folder, exist_ok=True)
        for mag in self.mags:
            urllib.request.urlretrieve(
                f"https://spire.embl.de/download_file/{mag}",
                path.join(mag_folder, "{mag}.fa.gz"),
            )

    def generate_manifest(self):
        manif = []
        reconstruction_folder = path.join(self.out_folder, "reconstructions/")
        for _, genome in self.mags.iterrows():
            manif.append(
                [
                    genome.genome_id,
                    genome.domain,
                    genome.phylum,
                    genome["class"],
                    genome.order,
                    genome.family,
                    genome.genus,
                    genome.species,
                    f"{reconstruction_folder}{genome.genome_id}.xml",
                    genome.derived_from_sample,
                ]
            )

        manifest = pd.DataFrame(
            manif,
            columns=[
                "id",
                "kingdom",
                "phylum",
                "class",
                "order",
                "family",
                "genus",
                "species",
                "file",
                "sample_id",
            ],
        )
        manifest.groupby("sample_id")
        return manifest

    def reconstruct(self, mag):
        reconstruction_folder = f"{self.out_folder}reconstructions/"
        os.makedirs(reconstruction_folder, exist_ok=True)
        input = f"{self.out_folder}mags/{mag}.fa.gz"
        output = f"{self.out_folder}reconstructions/{mag}.xml"
        command = f"carve --dna {input} --output {output} -i M9 -g M9 -v"
        subprocess.check_call(command, shell=True)
        return output
