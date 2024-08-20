from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, HRFlowable, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
import pandas as pd
import os

def generate_report(sample_name, output_path, kraken_report_file, logo_path):
    print(f"Generating PDF report for sample '{sample_name}'...")
    
    # Read the Kraken2 report file
    df = pd.read_csv(kraken_report_file, sep='\t', header=None)
    
    
    # Filter for the most confident hits where the third column is "G"
    confident_hits = df[(df[3] == "G") & (df[0] > 1.0)]
    
    # Sort by percentage in descending order
    confident_hits = confident_hits.sort_values(by=0, ascending=False)
    
    # Create a PDF report
    pdf_file = os.path.join(output_path, f"{sample_name}_kraken_report.pdf")
    doc = SimpleDocTemplate(pdf_file, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    # Add logo to the PDF
    if os.path.exists(logo_path):
        logo = Image(logo_path)
        logo.drawHeight = 0.5 * inch
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

    # Address text
    address = Paragraph("Laboratory of Nuqta Genomics<br/>Al-khobar, Saudi Arabia", getSampleStyleSheet()['Normal'])
    
    # Combine logo and address in a table
    header_table = Table([[logo, address]], colWidths=[5.5*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(header_table)
    elements.append(elements.append(HRFlowable(color=colors.black, thickness=1, width="100%", spaceBefore=12, spaceAfter=12)))

    
    # Add a title
    patient_info_file = os.path.join(output_path, f"{sample_name}.txt")
    patient_info_df = pd.read_csv(patient_info_file, sep='\t',  header=None)
    patient_info_df.columns = ['Attribute', 'Value']
    patient_info = patient_info_df.set_index('Attribute').T
    # Prepare the data for display
    data = [
    ["Name", "ID", "Age", "D.O.B", "D.O.T", "Location"],
    [patient_info["Name"].values[0], patient_info["ID"].values[0], patient_info["Age"].values[0],
    patient_info["D.O.B"].values[0], patient_info["D.O.T"].values[0], patient_info["Location"].values[0]]
    ]

    # Create the table to display the patient info
    table = Table(data, colWidths=[90, 90, 90])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    # Add the patient info table to the elements list
    elements.append(table)
    elements.append(elements.append(HRFlowable(color=colors.black, thickness=1, width="100%", spaceBefore=12, spaceAfter=12)))

    elements.append(Spacer(1, 12))
    
    # Add a table of confident hits
    table_data = [['% Reads', 'Reads', 'Taxon', 'Taxonomy']]
    for _, row in confident_hits.iterrows():
        table_data.append([f"{row[0]:.2f}%", row[1], row[3], row[5].strip()])
    
    table = Table(table_data, colWidths=[60, 60, 60, 60, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 340))
    
    # Add summary
    elements.append(elements.append(HRFlowable(color=colors.black, thickness=1, width="100%", spaceBefore=12, spaceAfter=12)))
    summary_text = (
        "Summary of Analysis:\n\n"
        "This report details the most confident taxonomic classifications based on the Kraken2 analysis of the basecalled reads. "
        "The analysis was conducted using a reference database specific to Leishmania species. "
        "The quality of the sequencing data was verified using NanoPlot, and the experiment proceeded only after verifying sufficient read count and quality.\n\n"
        "The key steps in this analysis included:\n"
        "1. Basecalling using high accuracy.\n"
        "2. Quality check to ensure read quality and quantity.\n"
        "3. Taxonomic classification using Kraken2.\n\n"
        "This report highlights the significant taxonomic hits with a confidence greater than 1% of the total reads."
    )
    elements.append(Paragraph(summary_text, styles['BodyText']))
    
    # Build the PDF
    doc.build(elements)
    print(f"PDF report generated successfully: {pdf_file}")

