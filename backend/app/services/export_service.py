import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_pdf(recommendation: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    green = colors.HexColor("#6a994e")

    title_style = ParagraphStyle("title", parent=styles["Title"], textColor=green, fontSize=18)
    h2_style = ParagraphStyle("h2", parent=styles["Heading2"], textColor=green)

    story = [
        Paragraph("AdSeason — Rapport de recommandations", title_style),
        Spacer(1, 0.4*cm),
        Paragraph(f"Saison : <b>{recommendation['season'].capitalize()}</b> | "
                  f"Budget total : <b>{recommendation['total_budget']} {recommendation['currency']}</b>",
                  styles["Normal"]),
        Spacer(1, 0.6*cm),
    ]

    for reco in recommendation["clusters"]:
        story.append(Paragraph(f"Cluster {reco['cluster_id']} — {reco['client_type']}", h2_style))
        story.append(Spacer(1, 0.2*cm))

        data = [
            ["Paramètre", "Valeur"],
            ["Profil client", reco["client_type"]],
            ["Catégorie produit", reco["product_category"]],
            ["Type d'offre", reco["offer_type"]],
            ["Canaux", ", ".join(reco["channels"])],
            ["Budget alloué", f"{reco['budget']} {reco['currency']}"],
            ["ROI estimé", f"x{reco['roi_estimate']}"],
            ["Audience cible", f"{reco['target_size']:,} clients ({reco['target_pct']}%)"],
        ]

        t = Table(data, colWidths=[6*cm, 11*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), green),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f0f7f0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

    doc.build(story)
    return buf.getvalue()
