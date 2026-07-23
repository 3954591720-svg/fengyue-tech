#!/usr/bin/env python3
"""
报价单 PDF 自动生成器
用法：python3 generate_quote.py <客户名> <项目名> <金额> [其他字段...]
"""

import sys
import os
from datetime import datetime

# 检查依赖
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib import colors
except ImportError:
    print("❌ 缺少 reportlab 依赖")
    print("安装命令：pip3 install reportlab")
    sys.exit(1)


def setup_chinese_font():
    """注册中文字体（跨平台兼容）"""
    import platform
    system = platform.system()

    font_paths = []

    if system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/Library/Fonts/Songti.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/msyh.ttc",
        ]
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                if font_path.endswith(".ttc"):
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                print(f"✅ 中文字体已注册：{font_path}")
                return "ChineseFont"
            except Exception as e:
                print(f"⚠️ 字体注册失败 {font_path}：{e}")
                continue

    print("⚠️ 未找到中文字体，PDF 中文可能乱码")
    print("请安装中文字体后重试")
    return None


def generate_quote(
    client_name,
    project_name,
    total_amount,
    items=None,
    valid_days=30,
    output_path=None,
):
    """生成报价单 PDF"""

    font_name = setup_chinese_font()
    if not font_name:
        return None

    if output_path is None:
        safe_client = "".join(c for c in client_name if c.isalnum() or c in "_-")
        safe_project = "".join(c for c in project_name if c.isalnum() or c in "_-")
        output_path = f"报价单_{safe_client}_{safe_project}_{datetime.now().strftime('%Y%m%d')}.pdf"

    # 创建 PDF 文档
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    elements = []
    styles = getSampleStyleSheet()

    # 自定义样式
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=24,
        textColor=colors.HexColor("#0066ff"),
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    h2_style = ParagraphStyle(
        "H2Style",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=14,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor("#374151"),
        leading=16,
    )

    # 标题
    elements.append(Paragraph("技 术 服 务 报 价 单", title_style))
    elements.append(Spacer(1, 0.5*cm))

    # 基本信息
    quote_no = f"FY-{datetime.now().strftime('%Y%m%d')}-{client_name[:3].upper()}"
    info_data = [
        ["报价单编号", quote_no, "报价日期", datetime.now().strftime("%Y 年 %m 月 %d 日")],
        ["客户名称", client_name, "有效期", f"{valid_days} 天"],
        ["项目名称", project_name, "报价单位", "宝鸡丰悦云创科技有限公司"],
    ]

    info_table = Table(info_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#374151")),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f8f9fa")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#f8f9fa")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.8*cm))

    # 报价明细
    elements.append(Paragraph("一、报价明细", h2_style))

    if items is None:
        items = [
            {"name": project_name, "desc": "详见技术方案", "unit_price": total_amount, "qty": 1}
        ]

    table_data = [["序号", "项目名称", "说明", "单价（元）", "数量", "小计（元）"]]
    for idx, item in enumerate(items, 1):
        subtotal = item["unit_price"] * item["qty"]
        table_data.append([
            str(idx),
            item["name"],
            item.get("desc", ""),
            f"{item['unit_price']:,.2f}",
            str(item["qty"]),
            f"{subtotal:,.2f}",
        ])
    table_data.append(["", "", "", "", "合计：", f"¥ {total_amount:,.2f}"])

    detail_table = Table(
        table_data,
        colWidths=[1.2*cm, 5*cm, 5*cm, 2.5*cm, 1.3*cm, 2.5*cm]
    )
    detail_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0066ff")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,0), "CENTER"),
        ("ALIGN", (0,1), (0,-1), "CENTER"),
        ("ALIGN", (3,1), (5,-1), "RIGHT"),
        ("ALIGN", (4,1), (4,-1), "CENTER"),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#f0f7ff")),
        ("FONTNAME", (4,-1), (5,-1), font_name),
        ("FONTSIZE", (4,-1), (5,-1), 11),
        ("TEXTCOLOR", (4,-1), (5,-1), colors.HexColor("#0066ff")),
        ("FONTWEIGHT", (4,-1), (5,-1), "BOLD"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 0.8*cm))

    # 服务说明
    elements.append(Paragraph("二、服务说明", h2_style))
    elements.append(Paragraph(
        f"1. 本报价为一次性技术服务费用，含 {total_amount*0.06:,.0f} 元增值税专用发票。",
        normal_style
    ))
    elements.append(Paragraph(
        f"2. 项目启动时间：首付款到账后 3 个工作日内。",
        normal_style
    ))
    elements.append(Paragraph(
        f"3. 详细技术方案见附件《技术方案说明书》。",
        normal_style
    ))
    elements.append(Paragraph(
        f"4. 验收合格后提供 3-6 个月免费维护期。",
        normal_style
    ))
    elements.append(Spacer(1, 0.5*cm))

    # 付款方式
    elements.append(Paragraph("三、付款方式", h2_style))
    if total_amount < 5000:
        payment_text = "一次性付款：合同签订后 3 日内支付全款。"
    elif total_amount < 50000:
        payment_text = "分期付款：合同签订后 3 日内支付 50% 预付款 ¥{:,.0f} 元，验收合格后 7 日内支付 50% 尾款 ¥{:,.0f} 元。".format(total_amount*0.5, total_amount*0.5)
    else:
        payment_text = "分期付款：30% 启动款 ¥{:,.0f} 元（合同签订后）+ 40% 中期款 ¥{:,.0f} 元（里程碑 1 验收后）+ 30% 尾款 ¥{:,.0f} 元（最终验收后）。".format(total_amount*0.3, total_amount*0.4, total_amount*0.3)
    elements.append(Paragraph(payment_text, normal_style))
    elements.append(Spacer(1, 0.5*cm))

    # 收款账户
    elements.append(Paragraph("四、收款账户", h2_style))
    account_data = [
        ["户名", "宝鸡丰悦云创科技有限公司"],
        ["开户行", "____________________（合同签订时确认）"],
        ["账号", "____________________"],
    ]
    account_table = Table(account_data, colWidths=[3*cm, 14*cm])
    account_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f8f9fa")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elements.append(account_table)
    elements.append(Spacer(1, 1*cm))

    # 备注
    elements.append(Paragraph("五、有效期与说明", h2_style))
    elements.append(Paragraph(
        f"1. 本报价单有效期至 {datetime.now().strftime('%Y 年 %m 月 %d 日')} 后 {valid_days} 天。",
        normal_style
    ))
    elements.append(Paragraph(
        "2. 双方签字盖章后，本报价单作为合同附件具有法律效力。",
        normal_style
    ))
    elements.append(Paragraph(
        "3. 详细权利义务以双方签订的《技术服务合同》为准。",
        normal_style
    ))
    elements.append(Spacer(1, 1.5*cm))

    # 签字栏
    sign_data = [
        ["", ""],
        ["客户确认：", "报价方："],
        ["", "宝鸡丰悦云创科技有限公司"],
        ["签字：_______________", "签字：_______________"],
        ["日期：_______________", "日期：_______________"],
    ]
    sign_table = Table(sign_data, colWidths=[8.5*cm, 8.5*cm], rowHeights=[0.5*cm, 0.6*cm, 0.5*cm, 1*cm, 0.6*cm])
    sign_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elements.append(sign_table)

    # 生成 PDF
    doc.build(elements)
    return output_path


def main():
    """CLI 入口"""
    if len(sys.argv) < 4:
        print("用法：python3 generate_quote.py <客户名> <项目名> <总金额> [明细...]")
        print("")
        print("示例：")
        print('  python3 generate_quote.py "某教育公司" "智能客服系统" 25000')
        print('  python3 generate_quote.py "某餐饮品牌" "会员小程序" 18000 "UI 设计" 5000 1 "前端开发" 8000 1 "后端 API" 5000 1')
        print("")
        print("明细格式：每 3 个参数一组（名称 单价 数量）")
        sys.exit(1)

    client_name = sys.argv[1]
    project_name = sys.argv[2]
    total_amount = float(sys.argv[3])

    items = None
    if len(sys.argv) > 4:
        items = []
        i = 4
        while i + 2 < len(sys.argv):
            try:
                items.append({
                    "name": sys.argv[i],
                    "unit_price": float(sys.argv[i+1]),
                    "qty": int(sys.argv[i+2]),
                })
                i += 3
            except ValueError:
                break

    output_path = generate_quote(client_name, project_name, total_amount, items)

    if output_path:
        abs_path = os.path.abspath(output_path)
        file_size = os.path.getsize(output_path)
        print(f"")
        print(f"✅ 报价单生成成功")
        print(f"📄 文件：{abs_path}")
        print(f"📦 大小：{file_size:,} 字节")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()