# Xopp Merger

## Description

`Xopp Merger` is a Python script designed to merge multiple `.xopp` files (used by [Xournal++](https://github.com/xournalpp/xournalpp)) with PDF backgrounds into a single `.xopp` file.

## Requirements

- Python 3.x
- Required Python packages: `glob`, `os`, `shutil`, `gzip`, `pikepdf`, `sys`, `natsort`

## Usage

- place merge-xopp.py in the same folder as the .xopp files. 
- run the script: 
```bash
python xopp_merger.py
```
- Done! you will find the output inside a new folder called `output-xopp-merger` together with the merged PDF background

The order of the merged files is alphabetical.

## Note
The script has not been tested extensively, feel free to report bugs.