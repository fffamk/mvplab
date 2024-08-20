#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import pandas as pd
from report import generate_report


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Nuqta Genome Analysis Pipeline"
    )
    
    parser.add_argument(
        "--sample-name", 
        required=True, 
        help="Name of the sample"
    )
    
    parser.add_argument(
        "--pod5-path", 
        required=True, 
        help="Path to the directory containing pod5 files"
    )
    
    parser.add_argument(
        "--output-path", 
        required=True, 
        help="Path to save the output files"
    )
    
    parser.add_argument(
        "--accuracy", 
        choices=['fast', 'hac', 'sup'], 
        default='fast', 
        help="Accuracy level for the analysis (default: fast)"
    )
    
    args = parser.parse_args()
    
    # Validate input paths
    if not os.path.exists(args.pod5_path):
        sys.exit(f"Error: The pod5 path '{args.pod5_path}' does not exist.")
    if not os.path.exists(args.output_path):
        sys.exit(f"Error: The output path '{args.output_path}' does not exist.")
    
    return args

def basecall(sample_name, pod5_path, output_path, accuracy):
    print(f"Running basecall on sample '{sample_name}' with accuracy '{accuracy}'...")
    
    # Define the path to the dorado binary
    dorado_path = "dependancies/basecalling/dorado/bin/dorado"
    
    # Construct the command
    command = [
        dorado_path, 
        "basecaller", 
        "--emit-fastq", 
        accuracy, 
        pod5_path
    ]
    
    # Redirect output to the specified output path
    output_file = os.path.join(output_path, f"{sample_name}_basecalled.fastq")
    
    try:
        with open(output_file, 'w') as output_handle:
            subprocess.run(command, stdout=output_handle, check=True)
        print(f"Basecalling completed successfully for sample '{sample_name}'. Output saved to '{output_file}'.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error during basecalling: {e}")
    except Exception as e:
        sys.exit(f"Unexpected error: {e}")


def quality_check(sample_name, output_path):
    print(f"Running quality check on sample '{sample_name}'...")
    
    # Define the path to the fastq file generated in the basecall step
    fastq_file = os.path.join(output_path, f"{sample_name}_basecalled.fastq")
    
    # Define the output directory for NanoPlot (where NanoStats.txt will be saved)
    qc_output_dir = os.path.join(output_path, "NanoPlot_output")
    os.makedirs(qc_output_dir, exist_ok=True)
    
    # Run NanoPlot to generate the quality check data
    try:
        subprocess.run([
            "NanoPlot",
            "--fastq", fastq_file,
            "--outdir", qc_output_dir,
            "--tsv_stats"
        ], check=True)
        print(f"Quality check completed for sample '{sample_name}'.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error during quality check: {e}")
    
    # Path to the NanoStats.txt file
    nanostats_file = os.path.join(qc_output_dir, "NanoStats.txt")
    
    # Read the NanoStats.txt file while ignoring lines that do not fit the expected format
    metrics = {}
    try:
        with open(nanostats_file, 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    key, value = parts
                    metrics[key] = value
        
        # Extract specific metrics
        number_of_reads = float(metrics.get("number_of_reads", 0))
        mean_qual = float(metrics.get("mean_qual", 0))
        
        # Print green checks based on conditions
        if number_of_reads > 10000:
            print("\u2705 Number of reads is greater than 10,000.")
        else:
            print("\u274C Number of reads is less than or equal to 10,000.")
        
        if mean_qual > 10:
            print("\u2705 Mean quality is greater than 10.")
        else:
            print("\u274C Mean quality is less than or equal to 10.")
    
    except FileNotFoundError:
        sys.exit(f"Error: NanoStats.txt not found in '{qc_output_dir}'.")
    except Exception as e:
        sys.exit(f"Unexpected error: {e}")

def search_db(sample_name, output_path):
    print(f"Running database search on sample '{sample_name}' using Kraken2...")
    
    # Define the path to the FASTQ file generated in the basecall step
    fastq_file = os.path.join(output_path, f"{sample_name}_basecalled.fastq")
    
    # Define the output file for Kraken2
    kraken_output = os.path.join(output_path, f"{sample_name}_kraken_report.txt")
    
    # Construct the Kraken2 command
    command = [
        "kraken2",
        "--db", "dependancies/kraken2_leishmania/",
        "--threads", "8",
        "--report", kraken_output,
        "--use-names",
        "--output", "tmp",
        fastq_file
    ]
    
    try:
        # Run the Kraken2 command
        subprocess.run(command, check=True)
        print(f"Database search completed successfully for sample '{sample_name}'.")
        generate_report(sample_name, output_path, kraken_output, "dependancies/nuqta.jpg")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error during database search: {e}")
    except Exception as e:
        sys.exit(f"Unexpected error: {e}")

def align(sample_name, output_path):
    print(f"Aligning sample '{sample_name}'...")
    # Implementation of alignment logic here
    pass

def main():
    args = parse_arguments()
    
    # Run the pipeline steps in sequence
    basecall(args.sample_name, args.pod5_path, args.output_path, args.accuracy)
    quality_check(args.sample_name, args.output_path)
    search_db(args.sample_name, args.output_path)
    align(args.sample_name, args.output_path)
    
    print(f"Pipeline completed successfully for sample '{args.sample_name}'.")

if __name__ == "__main__":
    main()
