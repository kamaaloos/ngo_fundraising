"""Print / PDF export for Reports charts (project + overall)."""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

from app.branding import COPYRIGHT_TEXT
from app.support_identity import get_install_id


def _figure_png_bytes(fig, *, dpi: int = 140) -> bytes:
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=dpi,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    return buf.getvalue()


def export_report_pdf(
    path: str | Path,
    *,
    title: str,
    subtitle: str,
    cards: list[tuple[str, str, str]],
    figures: list,
) -> Path:
    """Write a multi-page PDF: summary page + one chart per following page."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Image,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    file_path = Path(path)
    document = SimpleDocTemplate(
        str(file_path),
        pagesize=landscape(A4),
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#12233A"),
        spaceAfter=6,
    )
    sub_style = ParagraphStyle(
        "ReportSub",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#6B7A90"),
        spaceAfter=10,
    )
    foot_style = ParagraphStyle(
        "ReportFoot",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#6B7A90"),
    )

    story = []
    story.append(Paragraph(title.replace("\n", "<br/>"), title_style))
    story.append(Paragraph((subtitle or "").replace("\n", "<br/>"), sub_style))
    story.append(
        Paragraph(
            f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
            f"Install {get_install_id()}",
            foot_style,
        )
    )
    story.append(Spacer(1, 8))

    if cards:
        table_data = [["Metric", "Value", "Detail"]]
        for label, value, detail in cards:
            table_data.append([label, value, detail or ""])
        table = Table(table_data, colWidths=[45 * mm, 40 * mm, 160 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176B5B")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9E3F0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFD")]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 10))

    story.append(Paragraph(COPYRIGHT_TEXT, foot_style))

    page_w, page_h = landscape(A4)
    usable_w = page_w - 28 * mm
    usable_h = page_h - 40 * mm

    for index, fig in enumerate(figures, start=1):
        if fig is None:
            continue
        try:
            png = _figure_png_bytes(fig)
        except Exception:
            continue
        from reportlab.platypus import PageBreak

        story.append(PageBreak())
        chart_title = ""
        try:
            if fig.axes:
                chart_title = fig.axes[0].get_title() or f"Chart {index}"
        except Exception:
            chart_title = f"Chart {index}"
        story.append(Paragraph(chart_title, title_style))
        img = Image(io.BytesIO(png))
        # Fit chart into page while keeping aspect ratio.
        iw, ih = img.imageWidth, img.imageHeight
        scale = min(usable_w / iw, usable_h / ih, 1.0)
        img.drawWidth = iw * scale
        img.drawHeight = ih * scale
        story.append(img)

    document.build(story)
    return file_path


def print_report(
    parent,
    *,
    title: str,
    subtitle: str,
    cards: list[tuple[str, str, str]],
    figures: list,
) -> bool:
    """Open the system print dialog and print summary + charts."""
    from PySide6.QtGui import QImage, QPainter, QPageSize, QTextDocument
    from PySide6.QtPrintSupport import QPrintDialog, QPrinter
    from PySide6.QtCore import QMarginsF, Qt
    from PySide6.QtGui import QPageLayout

    if not figures and not cards:
        return False

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setPageOrientation(QPageLayout.Orientation.Landscape)
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    printer.setPageMargins(QMarginsF(12, 12, 12, 12), QPageLayout.Unit.Millimeter)

    dialog = QPrintDialog(printer, parent)
    dialog.setWindowTitle("Print report")
    if dialog.exec() != QPrintDialog.DialogCode.Accepted:
        return False

    painter = QPainter(printer)
    page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
    margin = int(page_rect.width() * 0.03)
    content = page_rect.adjusted(margin, margin, -margin, -margin)

    # Page 1 — text summary
    html_rows = "".join(
        f"<tr><td><b>{label}</b></td><td>{value}</td><td>{detail}</td></tr>"
        for label, value, detail in cards
    )
    html = f"""
    <h1>{title}</h1>
    <p>{subtitle}</p>
    <p><small>Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · Install {get_install_id()}</small></p>
    <table cellspacing="6" cellpadding="4" width="100%">
      <tr><th align="left">Metric</th><th align="left">Value</th><th align="left">Detail</th></tr>
      {html_rows}
    </table>
    <p><small>{COPYRIGHT_TEXT}</small></p>
    """
    doc = QTextDocument()
    doc.setHtml(html)
    doc.setPageSize(content.size())
    painter.save()
    painter.translate(content.topLeft())
    doc.drawContents(painter)
    painter.restore()

    for fig in figures:
        if fig is None:
            continue
        try:
            png = _figure_png_bytes(fig, dpi=160)
        except Exception:
            continue
        image = QImage.fromData(png, "PNG")
        if image.isNull():
            continue
        printer.newPage()
        scaled = image.scaled(
            content.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = content.x() + (content.width() - scaled.width()) // 2
        y = content.y() + (content.height() - scaled.height()) // 2
        painter.drawImage(x, y, scaled)

    painter.end()
    return True
