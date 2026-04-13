import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io
import os

st.set_page_config(page_title="Roku Nameplate Generator", page_icon="🏷️")
st.title("Roku Desk Nameplate Generator")

uploaded_file = st.file_uploader("Upload Employee List (Excel or CSV)", type=['csv', 'xlsx'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

    if st.button('Generate PDF'):
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        width, height = letter
        
        # Dimensions: 7.75" wide x 2" high
        np_w, np_h = 7.75 * inch, 2 * inch
        margin_x = (width - np_w) / 2
        y_pos = height - 1.25 * inch - np_h 

        logo_path = "Roku-Logo-Purple-Digital.jpg"

        for index, row in df.iterrows():
            # --- Draw Crop Marks ---
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.5)
            t_size = 0.2 * inch
            corners = [(margin_x, y_pos), (margin_x + np_w, y_pos), 
                       (margin_x, y_pos + np_h), (margin_x + np_w, y_pos + np_h)]
            for cx, cy in corners:
                c.line(cx - t_size, cy, cx + t_size, cy)
                c.line(cx, cy - t_size, cx, cy + t_size)

            # --- 1. Top-Left Logo Anchoring (Pushed Left 1/8") ---
            if os.path.exists(logo_path):
                logo_w = 1.8 * inch
                logo_h = 0.4 * inch
                # Pinned to top with 0.15" margin
                logo_y = (y_pos + np_h) - logo_h - (0.15 * inch)
                
                # X=0.0 to push left 1/8" from previous version
                c.drawImage(logo_path, margin_x + 0.0 * inch, logo_y, 
                            width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
            
            # --- 2. Name & Location Positioning ---
            baseline_y = y_pos + 0.35 * inch
            font_size = 26

            # Name: Bold (Left Justified at 0.25")
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", font_size)
            c.drawString(margin_x + 0.25 * inch, baseline_y, str(row['Name']))
            
            # Location: Regular (Right Justified at 0.25")
            c.setFont("Helvetica", font_size)
            loc_str = str(row['Desk Location'])
            text_w = c.stringWidth(loc_str, "Helvetica", font_size)
            c.drawString(margin_x + np_w - 0.25 * inch - text_w, baseline_y, loc_str)
            
            y_pos -= (np_h + 1.0 * inch)
            if y_pos < 1.0 * inch:
                c.showPage()
                y_pos = height - 1.25 * inch - np_h

        c.save()
        buf.seek(0)
        st.success("PDF Generated with Final Aligned Layout!")
        st.download_button("Download Final Nameplates", buf, "Roku_Final_Nameplates.pdf", "application/pdf")
