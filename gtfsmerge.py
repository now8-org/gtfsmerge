#!/usr/bin/env python3

"""Script to merge GTFS ZIP archives into one.

Usage: ./gtfsmerge.py gtfs1.zip gtfs2.zip gtfs3.zip output.zip

Features:
    * Uses the first archive contents as a reference.
    * Supports wildcards in input argumets.
    * Skips files from other archives with a different header.
    * Adds the CSV header row once per file in the output archive.
    * Avoids lines with duplicate indexes.

Note that the script doesn't check the input or output CSV files validity
nor GTFS compliance.
"""

import glob
import logging
import sys
import zipfile
from typing import Dict, List, Set

__author__ = "m0wer"
__copyright__ = "Copyright 2021, m0wer"
__license__ = "GPLv3"
__version__ = "1.2.0"
__maintainer__ = "m0wer"
__email__ = "m0wer@autistici.org"
__status__ = "Production"

FILE_INDEXES: Dict[str, List[str]] = {
    "agency.txt": ["agency_id"],
    "calendar.txt": ["service_id", "start_date", "end_date"],
    "calendar_dates.txt": ["service_id", "date"],
    "fare_attributes.txt": ["fare_id"],
    "fare_rules.txt": ["fare_id"],
    "feed_info.txt": ["feed_publisher_name"],
    "frequencies.txt": ["trip_id", "start_time"],
    "routes.txt": ["route_id"],
    "shapes.txt": ["shape_id", "shape_pt_sequence"],
    "stop_times.txt": ["trip_id", "stop_sequence"],
    "stops.txt": ["stop_id"],
    "trips.txt": ["trip_id"],
}


logging.basicConfig(
    format="[%(asctime)s] [%(levelname)8s] --- %(message)s",
    level=logging.INFO,
)


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
            logging.info("Processing %s...", gtfs_file)

            seen_lines: Set[bytes] = set()
            seen_ids: Set(tuple) = set()

            # open a file with the same name in the resulting zip
            with result.open(gtfs_file, "w") as result_gtfs_file:
                # start populating the output file with header of the
                # reference one (first argument)
                with zipfile.ZipFile(gtfs_archive_paths[0]).open(
                    gtfs_file
                ) as reference_gtfs_file:
                    logging.info("\tWriting header from reference...")
                    header: str = reference_gtfs_file.readline()
                    result_gtfs_file.write(header)
                    logging.debug("\t%s", header.decode("utf-8-sig"))
                non_duplicable_indexes_index: List[int] = []

                if gtfs_file not in FILE_INDEXES:
                    logging.warning("\t\tUsing first column as index.")
                    non_duplicable_indexes_index = [0]
                else:
                    for index in FILE_INDEXES[gtfs_file]:
                        non_duplicable_indexes_index.append(
                            header.decode("utf-8-sig")
                            .replace("\r\n", "")
                            .split(",")
                            .index(index)
                        )

                # loop through the zip files passed as arguments
                for gtfs_archive_path in gtfs_archive_paths:
                    logging.info("\t%s...", gtfs_archive_path)
                    # read the content of the current `gtfs_file` of each
                    with zipfile.ZipFile(gtfs_archive_path).open(
                        gtfs_file
                    ) as content:
                        if content.readline() == header:
                            for line in content:
                                index_tuple: tuple = tuple(
                                    line.decode("utf-8-sig")
                                    .replace("\r\n", "")
                                    .split(",")[index]
                                    for index in non_duplicable_indexes_index
                                )
                                if index_tuple not in seen_ids:
                                    result_gtfs_file.write(line)
                                    seen_lines.add(line)
                                    seen_ids.add(index_tuple)
                                else:
                                    if line in seen_lines:
                                        logging.debug(
                                            "\t\tAvoiding exact row duplicate"
                                            ": %s",
                                            line.decode("utf-8-sig"),
                                        )
                                    else:
                                        logging.info(
                                            "\t\tAvoiding row with duplicate "
                                            "IDs: %s",
                                            line.decode("utf-8-sig"),
                                        )

                        else:
                            logging.error(
                                "\t\tSkipping %s from %s "
                                "(header does not match the previous ones.",
                                gtfs_file,
                                gtfs_archive_path,
                            )


if __name__ == "__main__":
    main()
