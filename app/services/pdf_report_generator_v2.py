from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import logging
from pathlib import Path

class VehicleDamageReportGeneratorV2:
    def __init__(self):
        self.stylesheet = getSampleStyleSheet()
        self.styles = self.stylesheet['Normal'].clone('CustomNormal')  # Clone with a name
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        # Register fonts for currency symbol support
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'static/fonts/DejaVuSans.ttf'))
        except:
            logging.warning("DejaVuSans font not found, using Helvetica")
        
        # Colors from HTML
        self.PRIMARY_COLOR = colors.HexColor('#015386')  # ReadyAssist blue
        self.HEADER_BG = colors.HexColor('#FFF3D4')  # Light yellow
        self.GRAY_BG = colors.HexColor('#F3F4F6')  # Light gray
        
        # Create custom styles
        self.custom_styles = {}
        
        # Title style - keep original size for main header
        self.custom_styles['Title'] = ParagraphStyle(
            'CustomTitle',
            parent=self.stylesheet['Normal'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=0,
            spaceBefore=6,
            leading=28,
            alignment=0
        )
        
        # Subtitle style - keep original size for main header
        self.custom_styles['Subtitle'] = ParagraphStyle(
            'CustomSubtitle',
            parent=self.stylesheet['Normal'],
            fontName='Helvetica',
            fontSize=12,
            textColor=colors.gray,
            spaceAfter=0,
            spaceBefore=2,
            leading=14
        )
        
        # Section Header style - reduced size
        self.custom_styles['SectionHeader'] = ParagraphStyle(
            'CustomSectionHeader',
            parent=self.stylesheet['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,  # Reduced from 12
            textColor=colors.black,
            spaceBefore=6,  # Reduced from 10
            spaceAfter=3,  # Reduced from 5
            leading=12  # Reduced from 14
        )
        
        # Subsection Header style - reduced size
        self.custom_styles['SubsectionHeader'] = ParagraphStyle(
            'CustomSubsectionHeader',
            parent=self.stylesheet['Normal'],
            fontName='Helvetica',
            fontSize=9,  # Reduced from 11
            textColor=colors.gray,
            spaceBefore=6,  # Reduced from 10
            spaceAfter=4,  # Reduced from 8
            leading=11  # Reduced from 13
        )

    def _create_header(self, story):
        # Claims box with QR - styled to match the image exactly
        claims_box = Table(
            [
                [Paragraph("CLAIMS", 
                         ParagraphStyle('Claims',
                                      parent=self.stylesheet['Normal'],
                                      fontSize=10,
                                      textColor=colors.black,
                                      fontName='Helvetica-Bold',
                                      alignment=1,
                                      leading=12,
                                      spaceBefore=0,
                                      spaceAfter=0))],
                [Paragraph("QR", 
                         ParagraphStyle('QR',
                                      parent=self.stylesheet['Normal'],
                                      fontSize=10,
                                      textColor=colors.black,
                                      fontName='Helvetica',
                                      alignment=1,
                                      leading=12,
                                      spaceBefore=0,
                                      spaceAfter=0))]
            ],
            colWidths=[1.2*inch],
            rowHeights=[0.3*inch, 0.8*inch],
            style=TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ])
        )

        # Logo and company name
        try:
            logo_row = Table(
                [[
                    Image("static/images/readyassist_logo.png", width=0.3*inch, height=0.3*inch),
                    Paragraph("ReadyAssist", 
                            ParagraphStyle('Logo', 
                                         parent=self.stylesheet['Normal'],
                                         fontSize=18,
                                         textColor=colors.black,
                                         fontName='Helvetica-Bold',
                                         leading=18,
                                         spaceBefore=0,
                                         spaceAfter=0))
                ]],
                colWidths=[0.35*inch, 2*inch],
                style=TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ])
            )
        except:
            logo_row = Table(
                [[Paragraph("ReadyAssist", 
                          ParagraphStyle('Logo', 
                                       parent=self.stylesheet['Normal'],
                                       fontSize=18,
                                       textColor=colors.black,
                                       fontName='Helvetica-Bold',
                                       leading=18,
                                       spaceBefore=0,
                                       spaceAfter=0))]],
                colWidths=[2.35*inch],
                style=TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ])
            )

        # Create header content in a single table for better control
        header_content = [
            [logo_row, claims_box],
            [Paragraph("Comprehensive Vehicle Report", 
                      ParagraphStyle('CustomTitle',
                                   parent=self.stylesheet['Normal'],
                                   fontName='Helvetica-Bold',
                                   fontSize=20,
                                   textColor=colors.HexColor('#015386'),
                                   leading=22,
                                   spaceBefore=0,
                                   spaceAfter=0)), ''],
            [Paragraph("A system generated report by AI operated Impact Analysis system", 
                      ParagraphStyle('CustomSubtitle',
                                   parent=self.stylesheet['Normal'],
                                   fontName='Helvetica',
                                   fontSize=10,
                                   textColor=colors.gray,
                                   leading=12,
                                   spaceBefore=0,
                                   spaceAfter=0)), '']
        ]

        # Create the main header table with zero spacing
        header_table = Table(
            header_content,
            colWidths=[5.8*inch, 1.2*inch],
            rowHeights=[0.4*inch, 0.3*inch, 0.2*inch],  # Explicit row heights
            style=TableStyle([
                ('SPAN', (0, 1), (1, 1)),  # Span title across both columns
                ('SPAN', (0, 2), (1, 2)),  # Span subtitle across both columns
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ])
        )
        
        story.append(header_table)
        story.append(Spacer(1, 20))  # Space after header

    def _create_table_with_image(self, title, data, should_add_image_placeholder=False):
        elements = []
        elements.append(Paragraph(title, self.custom_styles['SectionHeader']))
        
        # Only create table if we have data beyond the header row
        if len(data) > 1:
            # Create main data table with full width if no image placeholder needed
            table = Table(
                data,
                colWidths=[2.5*inch, 4.5*inch] if not should_add_image_placeholder else [1.8*inch, 3.2*inch],
                style=TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.GRAY_BG),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                ])
            )
            
            if should_add_image_placeholder:
                # Create layout table with proper spacing and image placeholder
                layout_table = Table(
                    [[table, '', self._create_image_placeholder()]],
                    colWidths=[5*inch, 0.2*inch, 2*inch],
                    style=TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ])
                )
                elements.append(layout_table)
            else:
                elements.append(table)
                
        elements.append(Spacer(1, 12))
        return elements

    def _create_damage_analysis_section(self, story, data):
        story.append(Paragraph("Damage Analysis", self.custom_styles['SectionHeader']))
        damage_data = []
        damage_data.append(['Component', 'OBSERVATION', 'RECOMMENDATION'])
        
        damage_analysis = data.get('Damage Analysis', {})
        for component, details in damage_analysis.items():
            damage_data.append([
                Paragraph(component, ParagraphStyle('Component', 
                                                  parent=self.stylesheet['Normal'],
                                                  fontSize=8,
                                                  wordWrap='CJK')),
                Paragraph(details.get('Observation', 'N/A'), ParagraphStyle('Observation',
                                                                          parent=self.stylesheet['Normal'],
                                                                          fontSize=8,
                                                                          wordWrap='CJK')),
                Paragraph(details.get('Recommendation', 'N/A'), ParagraphStyle('Recommendation',
                                                                             parent=self.stylesheet['Normal'],
                                                                             fontSize=8,
                                                                             wordWrap='CJK'))
            ])
        
        # Create a table with space for image
        damage_table = Table(
            damage_data,
            colWidths=[1.6*inch, 1.6*inch, 1.8*inch],  # Reduced widths
            style=TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.GRAY_BG),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ])
        )
        
        # Create layout table with space for image
        layout_table = Table(
            [[damage_table, '']],
            colWidths=[5*inch, 2*inch],
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ])
        )
        story.append(layout_table)
        story.append(Spacer(1, 8))

    def _create_repair_costs_section(self, story, data):
        # Add page break before repair costs section
        story.append(PageBreak())
        story.append(Paragraph("Repair Cost Estimation", self.custom_styles['SectionHeader']))
        
        repair_costs = data.get('Repair Cost Estimation (INR)', {})
        if not repair_costs:
            return
            
        repair_data = [['Component', 'COST']]
        
        cost_style = ParagraphStyle(
            'Cost',
            parent=self.stylesheet['Normal'],
            fontSize=8,
            fontName='Helvetica',
            alignment=2
        )
        
        # Add all components except Total Repair Cost
        for component, cost in repair_costs.items():
            if component != 'Total Repair Cost':
                repair_data.append([
                    component,
                    Paragraph("Rs. " + "{:,}".format(cost) if isinstance(cost, (int, float)) else str(cost), cost_style)
                ])
        
        # Add Total Repair Cost at the end if it exists
        if 'Total Repair Cost' in repair_costs:
            repair_data.append([
                'Total Repair Cost',
                Paragraph("Rs. " + "{:,}".format(repair_costs['Total Repair Cost']), cost_style)
            ])
        
        # Create repair costs table with full width
        if len(repair_data) > 1:  # Only create table if we have data
            repair_table = Table(
                repair_data,
                colWidths=[5.5*inch, 1.5*inch],
                style=TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.GRAY_BG),
                    ('BACKGROUND', (0, -1), (-1, -1), self.GRAY_BG),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ])
            )
            story.append(repair_table)
            story.append(Spacer(1, 8))

    def _create_market_valuation_section(self, story, data):
        story.append(Paragraph("Market Valuation", self.custom_styles['SectionHeader']))
        
        # Create cost style for rupee values
        cost_style = ParagraphStyle(
            'Cost',
            parent=self.stylesheet['Normal'],
            fontSize=8,
            fontName='Helvetica',
            alignment=2  # Right alignment
        )
        
        # Main valuation table - dynamically create rows based on available data
        market_valuation = data.get('Market Valuation (INR)', {})
        valuation_data = [['Parameter', 'VALUE']]
        
        # Map of possible keys to their display names
        value_keys = {
            'Pre-Accident Value': 'Pre-Accident Value',
            'Post-Accident Value': 'Post-Accident Value',
            'Salvage Value': 'Salvage Value',
            'Estimated Value After Repairs': 'Estimated Value After Repairs'
        }
        
        # Only add rows for values that exist in the data
        for key, display_name in value_keys.items():
            if key in market_valuation:
                valuation_data.append([
                    display_name,
                    Paragraph("Rs. " + "{:,}".format(market_valuation.get(key, 0)), cost_style)
                ])
        
        if valuation_data:  # Only create table if we have data
            valuation_table = Table(
                valuation_data,
                colWidths=[4.5*inch, 2.5*inch],
                style=TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.GRAY_BG),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ])
            )
            story.append(valuation_table)
            story.append(Spacer(1, 4))
        
        # Market Quotes section - only add if quotes exist
        if market_valuation.get('Market Quotes'):
            story.append(Paragraph("Market Quotes", ParagraphStyle('SubsectionHeader',
                                                                parent=self.stylesheet['Normal'],
                                                                fontName='Helvetica-Bold',
                                                                fontSize=9,
                                                                textColor=colors.black,
                                                                spaceBefore=6,
                                                                spaceAfter=4,
                                                                leading=11)))
            quotes_data = [['Dealer', 'VALUE']]
            for quote in market_valuation.get('Market Quotes', []):
                if 'Dealer' in quote and 'Value' in quote:  # Only add complete quote entries
                    quotes_data.append([
                        Paragraph(quote.get('Dealer', 'N/A'), ParagraphStyle('Dealer',
                                                                        parent=self.stylesheet['Normal'],
                                                                        fontSize=10,
                                                                        wordWrap='CJK')),
                        Paragraph("Rs. " + "{:,}".format(quote.get('Value', 0)), cost_style)
                    ])
            
            if len(quotes_data) > 1:  # Only create table if we have quotes
                quotes_table = Table(
                    quotes_data,
                    colWidths=[4.5*inch, 2.5*inch],
                    style=TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), self.GRAY_BG),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ])
                )
                story.append(quotes_table)
                story.append(Spacer(1, 4))

    def _create_image_placeholders_grid(self, story):
        # Create a placeholder box for image
        def create_image_box():
            return Table(
                [['Image\nPlaceholder']],
                colWidths=[3.3*inch],
                rowHeights=[2.5*inch],
                style=TableStyle([
                    ('BOX', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                ])
            )

        # Create two rows of image placeholders
        row1 = Table(
            [[create_image_box(), '', create_image_box()]],
            colWidths=[3.3*inch, 0.4*inch, 3.3*inch],
            style=TableStyle([
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ])
        )
        
        # Add spacing between rows
        story.append(Spacer(1, 20))
        story.append(row1)
        story.append(Spacer(1, 20))
        
        row2 = Table(
            [[create_image_box(), '', create_image_box()]],
            colWidths=[3.3*inch, 0.4*inch, 3.3*inch],
            style=TableStyle([
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ])
        )
        
        story.append(row2)
        story.append(Spacer(1, 20))

    def _create_consistency_check_section(self, story, data):
        story.append(Paragraph("Vehicle Consistency Check", self.custom_styles['SectionHeader']))
        consistency_check = data.get('Vehicle Consistency Check', {})
        
        # Create a style for the reason text that handles wrapping
        reason_style = ParagraphStyle(
            'Reason',
            parent=self.stylesheet['Normal'],
            fontSize=10,
            wordWrap='CJK',
            alignment=0
        )
        
        consistency_data = [
            ['Parameter', 'DETAILS'],
            ['Same Vehicle Detected', 'Yes' if consistency_check.get('Same Vehicle Detected', False) else 'No'],
            ['Reason', Paragraph(consistency_check.get('Reason', 'N/A'), reason_style)]
        ]
        
        consistency_table = Table(
            consistency_data,
            colWidths=[2.5*inch, 4.5*inch],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.GRAY_BG),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ])
        )
        story.append(consistency_table)
        story.append(Spacer(1, 12))
        
        # Add the image placeholders grid after consistency check
        self._create_image_placeholders_grid(story)

    def _get_cell_style(self, alignment=0):
        """Get cell style with proper word wrapping
        alignment: 0=left, 1=center, 2=right"""
        return ParagraphStyle(
            'CellStyle',
            parent=self.stylesheet['Normal'],
            fontSize=8,
            wordWrap='CJK',
            alignment=alignment
        )

    def _format_value(self, value, align_right=False, is_boolean=False):
        """Format a value for display in a table cell"""
        if is_boolean:
            # Handle boolean values
            formatted = "Yes" if value else "No"
            return Paragraph(formatted, self._get_cell_style())
        elif isinstance(value, (int, float)):
            # Only format as currency if it's in a money context
            if align_right:
                formatted = "Rs. {:,}".format(value)
            else:
                formatted = "{:,}".format(value)
            return Paragraph(formatted, self._get_cell_style(alignment=2 if align_right else 0))
        elif isinstance(value, bool):
            # Handle boolean values
            formatted = "Yes" if value else "No"
            return Paragraph(formatted, self._get_cell_style())
        elif isinstance(value, list):
            # Handle list values
            if all(isinstance(item, dict) for item in value):
                # For list of dictionaries (e.g., market quotes), format each dict
                formatted_items = []
                for item in value:
                    if 'Dealer' in item and 'Value' in item:
                        formatted_items.append(f"{item['Dealer']}: Rs. {item['Value']:,}")
                    else:
                        # For other dictionary items, format key-value pairs
                        item_parts = []
                        for k, v in item.items():
                            if isinstance(v, bool):
                                v = "Yes" if v else "No"
                            item_parts.append(f"{k}: {v}")
                        formatted_items.append(", ".join(item_parts))
                formatted = "\n".join(formatted_items)
            else:
                # For simple lists, join with commas
                formatted = ", ".join(str(item) for item in value)
            return Paragraph(formatted, self._get_cell_style())
        elif isinstance(value, dict):
            # Handle dictionary values
            if 'Dealer' in value and 'Value' in value:
                # Special handling for market quote dictionaries
                formatted = f"{value['Dealer']}: Rs. {value['Value']:,}"
            elif 'Observation' in value or 'Recommendation' in value:
                # Return the raw dictionary for observation/recommendation pairs
                return value
            else:
                # For other dictionaries, format each key-value pair
                formatted_pairs = []
                for k, v in value.items():
                    if isinstance(v, bool):
                        formatted_pairs.append(f"{k}: {'Yes' if v else 'No'}")
                    elif isinstance(v, (int, float)) and any(word in k.lower() for word in ['cost', 'price', 'value']):
                        formatted_pairs.append(f"{k}: Rs. {v:,}")
                    else:
                        formatted_pairs.append(f"{k}: {v}")
                formatted = "\n".join(formatted_pairs)
            return Paragraph(formatted, self._get_cell_style())
        else:
            # Convert to string and wrap in Paragraph
            return Paragraph(str(value), self._get_cell_style())

    def generate_report(self, data, output_dir):
        """Generate a PDF report from the analysis data"""
        try:
            # Get the actual data from the structure
            report_data = data.get('data', {})
            
            # Create story (content)
            story = []
            self._create_header(story)
            
            # Process each top-level key in the JSON
            for section_key, section_data in report_data.items():
                # Skip empty sections
                if not section_data:
                    continue
                    
                # Add page break before Damage Analysis section
                if 'damage' in section_key.lower():
                    story.append(PageBreak())
                
                # Create section header using exact key name from JSON
                story.append(Paragraph(section_key, self.custom_styles['SectionHeader']))
                
                if isinstance(section_data, dict):
                    # Check if this is a damage analysis section
                    has_damage_format = any(
                        isinstance(v, dict) and ('Observation' in v or 'Recommendation' in v)
                        for v in section_data.values()
                    )
                    
                    # Determine if this section should have image placeholders
                    should_add_image = any(keyword in section_key.lower() for keyword in 
                        ['vehicle', 'damage', 'dashboard', 'condition', 'sticker', 'sign'])
                    
                    if has_damage_format:
                        # Create damage analysis table with three columns
                        table_data = [['Component', 'OBSERVATION', 'RECOMMENDATION']]
                        for component, details in section_data.items():
                            if isinstance(details, dict):
                                table_data.append([
                                    Paragraph(component, self._get_cell_style()),
                                    Paragraph(details.get('Observation', 'N/A'), self._get_cell_style()),
                                    Paragraph(details.get('Recommendation', 'N/A'), self._get_cell_style())
                                ])
                        if len(table_data) > 1:
                            table = Table(
                                table_data,
                                colWidths=[1.6*inch, 1.6*inch, 1.8*inch],
                                style=self._get_table_style(has_money=False)
                            )
                            if should_add_image:
                                # Create layout table with image placeholder
                                layout_table = Table(
                                    [[table, '', self._create_image_placeholder()]],
                                    colWidths=[5*inch, 0.2*inch, 2*inch],
                                    style=TableStyle([
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ])
                                )
                                story.append(layout_table)
                            else:
                                story.append(table)
                    else:
                        # Check if this is a cost/price section
                        is_money_section = any(word in section_key.lower() for word in ['cost', 'price', 'value', 'estimation'])
                        
                        # Standard key-value pairs
                        table_data = [['Parameter', 'DETAILS']]
                        for key, value in section_data.items():
                            # Determine if this is a boolean field
                            is_boolean = isinstance(value, bool) or key.lower() in ['same vehicle detected']
                            
                            # Format the value
                            formatted_value = self._format_value(
                                value,
                                align_right=is_money_section and isinstance(value, (int, float)),
                                is_boolean=is_boolean
                            )
                            
                            table_data.append([
                                Paragraph(str(key), self._get_cell_style()),
                                formatted_value
                            ])
                        
                        if len(table_data) > 1:
                            table = Table(
                                table_data,
                                colWidths=[3*inch, 4*inch] if not should_add_image else [2*inch, 3*inch],
                                style=self._get_table_style(has_money=is_money_section)
                            )
                            
                            if should_add_image:
                                # Create layout table with image placeholder
                                layout_table = Table(
                                    [[table, '', self._create_image_placeholder()]],
                                    colWidths=[5*inch, 0.2*inch, 2*inch],
                                    style=TableStyle([
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ])
                                )
                                story.append(layout_table)
                            else:
                                story.append(table)
                
                elif isinstance(section_data, list):
                    # Handle list data
                    if all(isinstance(item, dict) for item in section_data):
                        # List of dictionaries (e.g., market quotes)
                        if section_data and 'Dealer' in section_data[0]:
                            table_data = [['Dealer', 'VALUE']]
                            for item in section_data:
                                table_data.append([
                                    Paragraph(str(item.get('Dealer', 'N/A')), self._get_cell_style()),
                                    self._format_value(item.get('Value', 0), align_right=True)
                                ])
                        else:
                            # Generic list of dictionaries
                            keys = set().union(*(d.keys() for d in section_data))
                            table_data = [[Paragraph(k.upper(), self._get_cell_style(alignment=1)) for k in keys]]
                            for item in section_data:
                                row_data = []
                                for k in keys:
                                    value = item.get(k, 'N/A')
                                    is_boolean = isinstance(value, bool)
                                    row_data.append(self._format_value(value, is_boolean=is_boolean))
                                table_data.append(row_data)
                    else:
                        # Simple list
                        table_data = [[Paragraph('Item', self._get_cell_style(alignment=1))]]
                        for item in section_data:
                            is_boolean = isinstance(item, bool)
                            table_data.append([self._format_value(item, is_boolean=is_boolean)])
                    
                    if len(table_data) > 1:
                        col_width = 7*inch / len(table_data[0])
                        table = Table(
                            table_data,
                            colWidths=[col_width] * len(table_data[0]),
                            style=self._get_table_style(has_money=False)
                        )
                        story.append(table)
                
                story.append(Spacer(1, 12))
            
            # Add the image placeholders grid at the end
            self._create_image_placeholders_grid(story)
            
            # Generate the PDF
            filepath = os.path.join(output_dir, f"vehicle_damage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=25,
                leftMargin=25,
                topMargin=25,
                bottomMargin=45
            )
            
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            return filepath
            
        except Exception as e:
            logging.error(f"Error generating PDF report: {str(e)}")
            raise

    def _get_table_style(self, has_money=False):
        """Get consistent table styling
        has_money: True if the table contains monetary values (will right-align the last column)"""
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), self.GRAY_BG),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),  # Increased padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # Increased padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),  # Increased padding
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),  # Increased padding
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content to top
        ]
        
        if has_money:
            # Right align the last column for monetary values
            style.append(('ALIGN', (-1, 1), (-1, -1), 'RIGHT'))
            
        return TableStyle(style)

    def _create_image_placeholder(self):
        return Table(
            [['Image\nPlaceholder']],
            colWidths=[2*inch],
            rowHeights=[2*inch],
            style=TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ])
        )

    def _add_page_number(self, canvas, doc):
        canvas.saveState()
        # Create concise footer table
        footer_table = Table(
            [[
                # Company info in 3 lines
                Table(
                    [[
                        Paragraph(
                            "Sundaravijayam Automobile Services Private Limited",
                            ParagraphStyle('FooterCompany',
                                         parent=self.stylesheet['Normal'],
                                         fontSize=8,
                                         fontName='Helvetica-Bold')
                        )
                    ],
                    [
                        Paragraph(
                            "839/2, 24th Main Rd, Behind Thirumala Theatre, 1st Sector, HSR Layout, Bengaluru, Karnataka 560102",
                            ParagraphStyle('FooterAddress',
                                         parent=self.stylesheet['Normal'],
                                         fontSize=8,
                                         fontName='Helvetica',
                                         textColor=colors.gray)
                        )
                    ],
                    [
                        Paragraph(
                            '<link href="https://www.readyassist.in">www.readyassist.in</link>',
                            ParagraphStyle('FooterLink',
                                         parent=self.stylesheet['Normal'],
                                         fontSize=8,
                                         textColor=colors.blue,
                                         fontName='Helvetica')
                        )
                    ]],
                    style=TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                    ])
                ),
                Paragraph(
                    f"Page {canvas.getPageNumber()} of {doc.page}",
                    ParagraphStyle('PageNumber',
                                 parent=self.stylesheet['Normal'],
                                 fontSize=8,
                                 fontName='Helvetica',
                                 alignment=2)  # Right alignment
                )
            ]],
            colWidths=[5*inch, 2*inch],
            style=TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ('LEFTPADDING', (0, 0), (-1, -1), 30),
                ('RIGHTPADDING', (0, 0), (-1, -1), 30),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ])
        )
        
        # Position footer at bottom of page
        footer_table.wrapOn(canvas, doc.width, doc.bottomMargin)
        footer_table.drawOn(canvas, 0, doc.bottomMargin - 40)  # Adjusted position
        canvas.restoreState() 