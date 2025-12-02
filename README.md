# Shape Detector – Shape Similarity Analysis

This project provides tools for generating synthetic test images and analyzing objects
based on the geometric shape descriptor \( P^2 / A \).  
The program detects contours, computes shape ratios, groups similar objects, and
exports visualizations and summary reports.

## Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/) installed globally

## Installation

Install all dependencies using Poetry:

```bash
poetry install
```

## Usage

The CLI provides two main commands:

- **`generate`** – generates a synthetic test image
- **`analyze`** – analyzes an input image and produces visualizations and statistics

Display all CLI options:

```bash
poetry run python src/main.py -h
```

### Generate a test image

```bash
poetry run python src/main.py generate
```

This will create a synthetic test image in the default output directory.

### Analyze an image

```bash
poetry run python src/main.py analyze --image path/to/image.png
```

The analysis produces:

- edge detection output  
- grouped shapes visualization  
- normalized histograms  
- a summary table with statistics  
