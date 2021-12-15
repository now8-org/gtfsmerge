# GTFSmerge

Script to merge GTFS ZIP archives into one.

## Features

* Uses the first archive contents as a reference.
* Skips files from other archives with a different header.
* Adds the CSV header row once per file in the output archive.
* Avoids duplicate lines and prints them to stdout.

Note that the script doesn't check the input or output CSV files validity
nor GTFS compliance.

## Usage

```bash
./gtfsmerge.py gtfs1.zip gtfs2.zip gtfs3.zip output.zip
```
