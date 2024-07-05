# Xopp Merger

## Description

`Xopp Merger` is a Python script designed to merge multiple `.xopp` files (used by [Xournal++](https://github.com/xournalpp/xournalpp)) with PDF backgrounds into a single `.xopp` file.

## Requirements

- Python 3.x
- Required Python packages: `glob`, `os`, `shutil`, `gzip`, `pikepdf`, `sys`

## Usage

- place merge-xopp.py in the same folder as the .xopp files. 
- run the script: 
```bash
python xopp_merger.py
```

The order of the merged files is alphabetical.