#!/usr/bin/env python3
"""
发票 PDF 生成器（普通发票/增值税专用发票占位）
用法：
  python3 generate_invoice.py "客户名" "项目摘要" "金额" "税率" "发票号" [开票日期]
"""

import sys
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors


def setup_chinese_font():
    font_paths = []
    import platform
    system = platform.system()
    if system == "Darwin":
        font_paths = ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Light.ttc"]
    elif system == "Windows":
        font_paths = ["C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/msyh.ttc"]
    else:
        font_paths = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("CFont", fp, subfontIndex=0) if fp.endswith(".ttc") else TTFont("CFont", fp))
                return "CFont"
            except Exception:
                continue
    return None


def generate_invoice(client, item, amount, tax_rate, invoice_no, issue_date=None):
    font_name = setup_chinese_font()
    if not font_name:
        print("❌ 中文字体注册失败")
        return None

    if issue_date is None:
        issue_date = datetime.now().strftime("%Y 年 %m 月 %d 日")

    amount_excl_tax = amount / (1 + tax_rate / 100)
    tax_amount = amount - amount_excl_tax

    # 文件名
    safe = "".join(c for c in client if c.isalnum() or c in "_-")
    output_path = f"发票_{safe}_{invoice_no}.pdf"

    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("T", parent=styles["Title"], fontName=font_name, fontSize=24, textColor=colors.HexColor("#0066ff"), alignment=TA_CENTER, spaceAfter=8)
    subtitle_style = ParagraphStyle("S", parent=styles["Title"], fontName=font_name, fontSize=12, textColor=colors.HexColor("#6b7280"), alignment=TA_CENTER, spaceAfter=20)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontName=font_name, fontSize=12, textColor=colors.HexColor("#0066ff"), spaceBefore=10, spaceAfter=6)
    normal_style = ParagraphStyle("N", parent=styles["Normal"], fontName=font_name, fontSize=10, textColor=colors.HexColor("#374151"), leading=16)

    # 标题
    elements.append(Paragraph("发  票", title_style))
    elements.append(Paragraph("（用于客户报销 / 财务记账）", subtitle_style))

    # 发票基本信息
    info = [
        ["发票编号", invoice_no, "开票日期", issue_date],
    ]
    info_t = Table(info, colWidths=[2.5*cm, 6*cm, 2.5*cm, 6*cm])
    info_t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f8f9fa")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#f8f9fa")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elements.append(info_t)
    elements.append(Spacer(1, 0.5*cm))

    # 销售方/购买方
    elements.append(Paragraph("销售方信息", h2_style))
    seller_data = [
        ["名称", "宝鸡丰悦云创科技有限公司"],
        ["纳税人识别号", "____________________（待税局核定后填写）"],
        ["地址、电话", "陕西省宝鸡市渭滨区高新开发区 / ____________________"],
        ["开户行及账号", "____________________"],
    ]
    seller_t = Table(seller_data, colWidths=[3*cm, 14*cm])
    seller_t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f8f9fa")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(seller_t)
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("购买方信息", h2_style))
    buyer_data = [
        ["名称", client],
        ["纳税人识别号", "____________________"],
        ["地址、电话", "____________________"],
        ["开户行及账号", "____________________"],
    ]
    buyer_t = Table(buyer_data, colWidths=[3*cm, 14*cm])
    buyer_t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f8f9fa")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(buyer_t)
    elements.append(Spacer(1, 0.5*cm))

    # 货物明细
    elements.append(Paragraph("货物或应税劳务清单", h2_style))
    items_data = [
        ["序号", "货物/劳务名称", "数量", "单价（元）", "金额（元）", "税率", "税额（元）"],
        ["1", item, "1", f"{amount_excl_tax:,.2f}", f"{amount_excl_tax:,.2f}", f"{tax_rate}%", f"{tax_amount:,.2f}"],
        ["合计", "", "", "", f"{amount_excl_tax:,.2f}", "", f"{tax_amount:,.2f}"],
    ]
    items_t = Table(
        items_data,
        colWidths=[1.2*cm, 5*cm, 1.3*cm, 2.5*cm, 2.5*cm, 1.5*cm, 2.5*cm]
    )
    items_t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0066ff")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,0), "CENTER"),
        ("ALIGN", (0,1), (0,-1), "CENTER"),
        ("ALIGN", (2,1), (2,-1), "CENTER"),
        ("ALIGN", (5,1), (5,-1), "CENTER"),
        ("ALIGN", (3,1), (6,-1), "RIGHT"),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#f0f7ff")),
        ("FONTWEIGHT", (0,-1), (-1,-1), "BOLD"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elements.append(items_t)
    elements.append(Spacer(1, 0.5*cm))

    # 价税合计
    total_data = [
        ["价税合计（大写）", "____________________"],
        ["价税合计（小写）", f"¥ {amount:,.2f}"],
    ]
    total_t = Table(total_data, colWidths=[5*cm, 12*cm])
    total_t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 11),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f8f9fa")),
        ("BACKGROUND", (0,1), (-1,1), colors.HexColor("#fef3c7")),
        ("FONTWEIGHT", (0,1), (-1,1), "BOLD"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    elements.append(total_t)
    elements.append(Spacer(1, 0.5*cm))

    # 备注
    elements.append(Paragraph("备注", h2_style))
    elements.append(Paragraph(
        "1. 本发票为电子发票，请妥善保管。<br/>"
        "2. 如有问题请联系：3954591720@qq.com<br/>"
        "3. 发票内容对应双方签订的服务合同。",
        normal_style
    ))
    elements.append(Spacer(1, 1.5*cm))

    # 签字盖章
    sign_data = [
        ["销售方盖章：", "开票人："],
        ["宝鸡丰悦云创科技有限公司", ""],
        ["", ""],
        ["____________________", "____________________"],
    ]
    sign_t = Table(sign_data, colWidths=[10*cm, 7*cm], rowHeights=[0.5*cm, 0.5*cm, 0.3*cm, 1*cm])
    sign_t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 2),
    ]))
    elements.append(sign_t)

    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph(
        f"<para align='center'><font size=8 color='#9ca3af'>发票编号：{invoice_no} · 开票日期：{issue_date}</font></para>",
        normal_style
    ))

    doc.build(elements)
    return output_path


def main():
    if len(sys.argv) < 6:
        print("用法：python3 generate_invoice.py <客户名> <项目摘要> <含税总额> <税率%> <发票号> [开票日期]")
        print("")
        print("示例：")
        print('  python3 generate_invoice.py "某教育公司" "技术服务费" 16800 6 "20260724001"')
        print('  python3 generate_invoice.py "某餐饮品牌" "小程序开发费" 18000 6 "20260724002" "2026年7月24日"')
        print("")
        print("税率：一般纳税人 6%（技术服务）/ 13%（硬件）/ 3%（小规模）")
        sys.exit(1)

    client = sys.argv[1]
    item = sys.argv[2]
    amount = float(sys.argv[3])
    tax_rate = float(sys.argv[4])
    invoice_no = sys.argv[5]
    issue_date = sys.argv[6] if len(sys.argv) > 6 else None

    path = generate_invoice(client, item, amount, tax_rate, invoice_no, issue_date)
    if path:
        print(f"")
        print(f"✅ 发票生成成功")
        print(f"📄 文件：{os.path.abspath(path)}")
        print(f"📦 大小：{os.path.getsize(path):,} 字节")


if __name__ == "__main__":
    main()