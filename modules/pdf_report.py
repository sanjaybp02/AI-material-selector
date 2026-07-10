from fpdf import FPDF


def sanitize_latin1(text):
    """
    Safely encode string to latin-1 by replacing unsupported characters
    like Rupee symbol, smart quotes, em-dashes, and bullet points.
    """
    if not isinstance(text, str):
        text = str(text)
    
    replacements = {
        "₹": "INR ",
        "\u201d": '"',    # Right double quote
        "\u201c": '"',    # Left double quote
        "\u2019": "'",    # Smart single quote / apostrophe
        "\u2018": "'",    # Smart single quote
        "\u2014": " - ",  # Em dash
        "\u2013": " - ",  # En dash
        "\u2022": " - ",  # Bullet point
        "\u2713": "Yes",  # Checkmark
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
        
    return text.encode("latin-1", errors="replace").decode("latin-1")


def create_pdf(material_name, confidence, reasoning, cost, mass, volume, currency="₹", material_properties=None, carbon_footprint=None, carbon_unit="kg CO2"):
    """Generate a PDF engineering report and return bytes."""
    # Sanitize inputs to prevent FPDFUnicodeEncodingExceptions
    material_name = sanitize_latin1(material_name)
    reasoning = sanitize_latin1(reasoning)
    pdf_currency = "INR " if currency == "₹" else sanitize_latin1(currency)
    carbon_unit = sanitize_latin1(carbon_unit)

    pdf = FPDF()
    pdf.add_page()
    
    # Mock Branding
    pdf.set_fill_color(0, 229, 255) # Accent color
    pdf.rect(0, 0, 210, 20, 'F')
    pdf.set_y(5)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(200, 10, txt="AI Material Selector", ln=True, align='L')
    
    pdf.set_y(30)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Material Recommendation Report", ln=True, align='C')

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Material: {material_name}", ln=True, align='L')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Confidence: {confidence}%", ln=True, align='L')

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Part specifications", ln=True, align='L')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Volume: {volume} cm3" if carbon_unit == "kg CO2" else f"Volume: {volume} in3", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Mass: {mass:.2f} kg" if carbon_unit == "kg CO2" else f"Mass: {mass:.2f} lb", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Raw material cost: {pdf_currency}{cost:.2f}", ln=True, align='L')
    if carbon_footprint is not None:
        pdf.cell(200, 10, txt=f"Calculated carbon footprint: {carbon_footprint:.3f} {carbon_unit}", ln=True, align='L')

    if material_properties is not None:
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Key Properties", ln=True, align='L')
        pdf.set_font("Arial", '', 10)
        
        # Simple table
        col_width = pdf.w / 2.2
        th = pdf.font_size * 1.5
        for k, v in material_properties.items():
            if str(v).lower() != 'nan':
                clean_k = sanitize_latin1(k)
                clean_v = sanitize_latin1(v)
                pdf.cell(col_width, th, clean_k, border=1)
                pdf.cell(col_width, th, clean_v, border=1)
                pdf.ln(th)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Engineering reasoning", ln=True, align='L')
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, txt=reasoning)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(200, 10, txt="Assumptions & Limitations", ln=True, align='L')
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 6, txt="This report was generated using AI. The estimates for cost, mass, carbon footprint, and performance are approximations based on idealized part volumes. Always verify with manufacturer datasheets before production.")

    return bytes(pdf.output())
