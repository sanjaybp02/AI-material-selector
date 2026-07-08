from fpdf import FPDF


def create_pdf(material_name, confidence, reasoning, cost, mass, volume, currency="₹"):
    """Generate a PDF engineering report and return bytes."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Engineering Material Recommendation Report", ln=True, align='C')

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Recommended Material: {material_name}", ln=True, align='L')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"AI Confidence Score: {confidence}%", ln=True, align='L')

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Part Specifications:", ln=True, align='L')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Estimated Volume: {volume} cm3", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Estimated Mass: {mass:.2f} kg", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Estimated Raw Material Cost: {currency}{cost:.2f}", ln=True, align='L')

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Engineering Reasoning:", ln=True, align='L')
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, txt=reasoning)

    return bytes(pdf.output())
