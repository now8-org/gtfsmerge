#!/usr/bin/env python3

"""Script to merge GTFS ZIP archives into one.

Usage: ./gtfsmerge.py gtfs1.zip gtfs2.zip gtfs3.zip output.zip

Features:
    * Uses the first archive contents as a reference.
    * Skips files from other archives with a different header.
    * Adds the CSV header row once per file in the output archive.
    * Avoids duplicate lines and prints them to stdout.

Note that the script doesn't check the input or output CSV files validity
nor GTFS compliance.
"""

import glob
import sys
import zipfile
from typing import List

__author__ = "m0wer"
__copyright__ = "Copyright 2021, m0wer"
__license__ = "GPLv3"
__version__ = "1.1.0"
__maintainer__ = "m0wer"
__email__ = "m0wer@autistici.org"
__status__ = "Production"


def main():
    """Run the program."""
    gtfs_archive_paths: str = [
        path for arg in sys.argv[1:-1] for path in glob.glob(arg)
    ]
    output_path: str = sys.argv[-1]

    if len(gtfs_archive_paths) < 1:
        raise ValueError("Missing arguments.")

    with zipfile.ZipFile(output_path, "w") as result:
        # get list of files in the first zip as reference
        with zipfile.ZipFile(gtfs_archive_paths[0]) as reference_gtfs:
            zipfile_namelist: List[str] = reference_gtfs.namelist()

        for gtfs_file in zipfile_namelist:
            print(f"Processing {gtfs_file}...")
            # open a file with the same name in the resulting zip
            with result.open(gtfs_file, "w") as result_gtfs_file:
                seen_lines: set = set()
                # start populating the output file with the contents of the
                # reference one (first argument)
                with zipfile.ZipFile(gtfs_archive_paths[0]).open(
                    gtfs_file
                ) as reference_gtfs_file:
                    print(f"\t{gtfs_archive_paths[0]} (reference)...")
                    header: str = reference_gtfs_file.readline()
                    result_gtfs_file.write(header)
                    for line in reference_gtfs_file:
                        result_gtfs_file.write(line)
                        seen_lines.add(line)
                # loop through the zip files passed as arguments
                for gtfs_archive_path in gtfs_archive_paths[1:]:
                    print(f"\t{gtfs_archive_path}...")
                    # read the content of the current `gtfs_file` of each
                    with zipfile.ZipFile(gtfs_archive_path).open(gtfs_file) as content:
                        if content.readline() == header:
                            for line in content:
                                if line not in seen_lines:
                                    result_gtfs_file.write(line)
                                else:
                                    print(f"\t\tAvoiding duplicate line:\n\t{line}")
                        else:
                            print(
                                f"\t\tSkipping {gtfs_file} from {gtfs_archive_path} "
                                f"(header does not match the previous ones."
                            )


if __name__ == "__main__":
    main()
