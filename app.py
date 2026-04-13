import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import io

# Page Configuration
st.set_page_config(page_title="Roku Nameplate Generator", page_icon="🏷️")
st.title("Roku Desk Nameplate Generator")
st.markdown("Upload your employee Excel/CSV to generate 8x2 formatted nameplates with crop marks.")

# 1. File Uploader
uploaded_file = st.file_uploader("Upload Employee List (Excel or CSV)", type=['csv', 'xlsx'])

if uploaded_file:
    # Read data based on file type
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Preview of data:", df.head())

    if st.button('Generate PDF'):
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        width, height = letter
        
        # Brand & Layout Specs
        roku_purple = HexColor("#662D91")
        np_w, np_h = 8 * inch, 2 * inch
        margin_x = (width - np_w) / 2
        y_pos = height - 1.25 * inch - np_h  # Start near top

        for index, row in df.iterrows():
            # Draw Corner Tick Marks (For Cutting)
            c.setStrokeColorRGB(0.8, 0.8, 0.8) # Light grey ticks
            c.setLineWidth(0.5)
            tick_size = 0.2 * inch
            # Coordinates for the 4 corners
            corners = [(margin_x, y_pos), (margin_x + np_w, y_pos), 
                       (margin_x, y_pos + np_h), (margin_x + np_w, y_pos + np_h)]
            for cx, cy in corners:
                c.line(cx - tick_size, cy, cx + tick_size, cy) # Horiz
                c.line(cx, cy - tick_size, cx, cy + tick_size) # Vert

            # Header: ROKU Logo (Upper Left)
            c.setFillColor(roku_purple)
            c.setFont("Helvetica-Bold", 20)
            c.drawString(margin_x + 0.4 * inch, y_pos + np_h - 0.6 * inch, "Roku")
            
            # Name: Justified Left (Under Logo)
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", 26)
            baseline_y = y_pos + 0.5 * inch
            c.drawString(margin_x + 0.4 * inch, baseline_y, str(row['Name']))
            
            # Location: Justified Right (Same height as name)
            c.setFont("Helvetica", 18)
            loc_str = str(row['Desk Location'])
            text_w = c.stringWidth(loc_str, "Helvetica", 18)
            c.drawString(margin_x + np_w - 0.4 * inch - text_w, baseline_y, loc_str)
            
            # Advance to next nameplate slot
            y_pos -= (np_h + 1.0 * inch) # 1 inch gap between plates
            
            # Check if we need a new page
            if y_pos < 1.0 * inch:
                c.showPage()
                y_pos = height - 1.25 * inch - np_h

        c.save()
        buf.seek(0)
        
        st.success("Success! Your PDF is ready.")
        st.download_button(
            label="Download Nameplates PDF",
            data=buf,
            file_name="Roku_Bulk_Nameplates.pdf",
            mime="application/pdf"
        )