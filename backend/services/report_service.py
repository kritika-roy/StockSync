import os

import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

def generate_report(data):
    ai_text = data.get("ai_insights",None)
    file_path = os.path.join(os.getcwd(), "Business_Report.pdf")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    chart_path = os.path.join(BASE_DIR, "demand_chart.png")

    # ---------- CREATE DEMAND CHART ----------
    products = list(data["demand_data"].keys())
    values = [
    (v.get("Predicted Daily Demand", 0) if isinstance(v, dict) else 0)
    for v in data["demand_data"].values()
    ]

    plt.figure(figsize=(6, 3))
    plt.bar(products, values)
    plt.title("Predicted Demand")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    # ---------- PDF ----------
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    elements = []

    # ---------- TITLE ----------
    elements.append(Paragraph(
        "<b><font size=20 color='green'>StockSync AI Report</font></b>",
        styles["Title"]
    ))
    elements.append(Spacer(1, 20))

    # ---------- KPI CARDS ----------
    kpi_data = [
        ["Revenue (Rs.)", "Reorders", "Expiry Risk"],
        [
            f"{data['total_revenue']}",
            data["reorder_count"],
            data["expiry_count"]
        ]
    ]

    kpi_table = Table(kpi_data, colWidths=[150, 150, 150])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.darkgreen),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("BACKGROUND", (0,1), (-1,1), colors.lightgrey),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ]))

    elements.append(kpi_table)
    elements.append(Spacer(1, 20))

    # ---------- ALERTS ----------
    elements.append(Paragraph("<b> Critical Alerts</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    for product, d in data["inventory_data"].items():
        if d.get("Status") in ["REORDER", "Restock Needed"]:
            elements.append(Paragraph(f" {product} → Reorder Needed", styles["Normal"]))

    for product, d in data["expiry_data"].items():
        if d.get("Status") in ["Expiry Risk", "High Risk"]:
            elements.append(Paragraph(f" {product} → Expiry Risk", styles["Normal"]))

    elements.append(Spacer(1, 20))

    # ---------- CHART ----------
    elements.append(Paragraph("<b> Demand Forecast</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(Image(chart_path, width=400, height=200))
    elements.append(Spacer(1, 20))

    # ---------- INSIGHTS ----------
    elements.append(Paragraph("<b> Business Insights</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    for product, d in data["demand_data"].items():
        demand = d.get("Predicted Daily Demand", 0)

        if demand > 50:
            text = f"{product}: High demand → Increase stock"
        elif demand < 20:
            text = f"{product}: Low demand → Reduce stock"
        else:
            text = f"{product}: Stable demand"

        elements.append(Paragraph(f"• {text}", styles["Normal"]))

    elements.append(Spacer(1, 20))

    # ---------- INVENTORY TABLE ----------
    elements.append(Paragraph("<b> Inventory Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    table_data = [["Product", "Stock", "Status"]]

    for product, d in data["inventory_data"].items():
        table_data.append([
            product,
            d.get("Current Stock", 0),
            d.get("Status", "Unknown")
        ])

    inv_table = Table(table_data)
    inv_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.green),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
    ]))

    elements.append(inv_table)
    elements.append(Spacer(1, 20))

    # ---------- AI SECTION (IMPORTANT) ----------
    if ai_text:
        elements.append(Paragraph("AI Insights", styles['Heading2']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(ai_text, styles['Normal']))

    # ---------- BUILD ----------
    doc.build(elements)

    return file_path