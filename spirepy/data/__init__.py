import pandas as pd
from os.path import split, join

this_dir, _ = split(__file__)

genome_metadata = pd.read_csv(
    join(this_dir, "spire_v1_genome_metadata.tsv.gz"), sep="\t"
)
