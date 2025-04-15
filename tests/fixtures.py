import pytest
import os.path as path

from spirepy import Sample, Study

this_dir, _ = path.split(__file__)


@pytest.fixture
def study():
    return Study(
        name="Minot_2013_gut_phage",
        out_folder=path.join(this_dir, "data/Minot_2013_gut_phage"),
    )


@pytest.fixture
def sample():
    return study.samples[0]
