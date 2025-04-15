import pytest
import os.path as path

from spirepy import Study
from spirepy.sample import Sample

this_dir, _ = path.split(__file__)


@pytest.fixture
def study():
    "A simple study from the SPIRE database"
    return Study(
        name="Minot_2013_gut_phage",
        out_folder=path.join(this_dir, "data/Minot_2013_gut_phage"),
    )
