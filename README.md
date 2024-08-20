# Nuqta Genome Analysis Pipeline Software

## Overview
This software is designed to automate a comprehensive genome analysis pipeline. The pipeline processes genomic data from raw `pod5` files through several key steps including basecalling, quality control, database searching, and reporting. The software integrates essential tools like Kraken2 for taxonomic classification, NanoPlot for quality analysis, and generates a detailed PDF report summarizing the results, including confident hits and patient information.

### Key Features
- **Automated Pipeline:** Executes all steps in sequence from basecalling to report generation.
- **Quality Control:** Ensures data quality with NanoPlot before proceeding with the analysis.
- **Taxonomic Classification:** Uses Kraken2 for highly accurate taxonomic classification based on a specified database.
- **Report Generation:** Produces a well-formatted PDF report including taxonomic hits, quality metrics, and patient details.

## Installation

To run this software, you will need to set up a Conda environment with the required dependencies. Follow these steps:

### Step 1: Install Conda
If you do not have Conda installed, please download and install it from [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution).

### Step 2: Create the Conda Environment
Create and activate a Conda environment with Python 3.9 and the necessary dependencies:

```bash
conda create -n genome_pipeline python=3.9
conda activate genome_pipeline
conda install -c bioconda kraken2 nanoplot
pip install pandas numpy reportlab
```

### Step 3: Clone the Repository
Clone the software repository from GitHub:

```bash
git clone REPOSITORY_URL
cd MVP
```

## Kraken2 Database Setup
Building a Custom Kraken2 Database

To use Kraken2 for taxonomic classification, you need to build a custom database or use an existing one. To build a custom Kraken2 database, follow these steps:

1. Download and Prepare the Sequences:
Download the sequences you want to include in your database.
```bash
kraken2-build --download-library <library_name> --db <database_name>
```
2. Build the Database:
```bash
kraken2-build --build --db <database_name>
```

### Download Leishmania Database for Demo
To run the demo, download the pre-built Leishmania database from Google Drive link.
then decompress with (uncompressed size ~45 Gb):
```bash
tar -xJf leshmania_db.tar.xz -C dependancies/
```

### Download Dorado
Download the latest verison of Dorado and place it  dependancies/basecalling

## Software Workflow
1. Basecalling
The software runs a basecaller using Dorado to process raw pod5 files into FASTQ format
2. Quality Check
Next, the software uses NanoPlot to check the quality of the FASTQ data. It ensures that the number of reads is greater than 10,000 and the mean quality score exceeds 10 before proceeding.
3. Database Search with Kraken2
The software runs Kraken2 using the specified database to classify the reads
4. Report Generation
Finally, a detailed PDF report is generated, which includes:
    - The most confident taxonomic hits based on percentage and classification.
    - Quality control metrics.
    - Patient information displayed in a structured table.

## Usage
To run the pipeline, use the following command from the terminal:
```bash
python run_pipeline.py --sample-name SAMPLE_NAME --pod5-path /path/to/pod5/files --output-path /path/to/output --accuracy high
```