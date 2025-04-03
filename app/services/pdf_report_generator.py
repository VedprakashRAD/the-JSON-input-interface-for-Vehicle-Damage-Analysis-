import os
from typing import Dict, Any
from pathlib import Path
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class VehicleDamageReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
    def generate_report(self, analysis_data: Dict[str, Any], output_dir: str) -> str:
        """
        Generate a PDF report from the analysis data using reportlab
        """
        try:
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate PDF filename
            pdf_filename = f"vehicle_damage_report_{analysis_data['order_id']}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            # Create the PDF document
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build the PDF content
            story = []
            
            # Add title
            title = Paragraph(f"Vehicle Damage Assessment Report", self.title_style)
            story.append(title)
            
            # Add order ID
            order_id = Paragraph(f"Order ID: {analysis_data['order_id']}", self.styles['Heading2'])
            story.append(order_id)
            story.append(Spacer(1, 20))
            
            # Add summary table
            summary_data = [
                ['Total Images', str(analysis_data['total_images'])],
                ['Processed Images', str(analysis_data['processed_images'])]
            ]
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (1, 0), (-1, -1), colors.beige),
                ('TEXTCOLOR', (1, 0), (-1, -1), colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 30))
            
            # Add analysis results
            for result in analysis_data['results']:
                # Add section title
                analysis_title = Paragraph("Analysis Results", self.styles['Heading2'])
                story.append(analysis_title)
                story.append(Spacer(1, 10))
                
                # Add analysis table
                analysis_data = [
                    ['Damage Detected', str(result['analysis']['damage_detected'])],
                    ['Severity', result['analysis']['damage_severity']],
                    ['Affected Areas', ', '.join(result['analysis']['affected_areas'])],
                    ['Estimated Cost', result['analysis']['estimated_repair_cost']]
                ]
                analysis_table = Table(analysis_data)
                analysis_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (1, 0), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (1, 0), (-1, -1), colors.black),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(analysis_table)
                story.append(Spacer(1, 20))
                
                # Add recommendations
                rec_title = Paragraph("Recommendations", self.styles['Heading3'])
                story.append(rec_title)
                for rec in result['analysis']['recommendations']:
                    rec_text = Paragraph(f"• {rec}", self.styles['Normal'])
                    story.append(rec_text)
                story.append(Spacer(1, 30))
            
            # Build the PDF
            doc.build(story)
            
            logging.info(f"Generated PDF report at: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logging.error(f"Error generating PDF report: {str(e)}")
            raise 