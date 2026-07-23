#!/usr/bin/env python3
"""
技术服务合同 PDF 生成器
用法：python3 generate_contract.py <甲方公司名> <项目名> <总金额> [联系人] [联系电话] [邮箱]
"""

import sys
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors


def setup_chinese_font():
    import platform
    system = platform.system()
    font_paths = []
    if system == "Darwin":
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
        ]
    elif system == "Windows":
        font_paths = ["C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/msyh.ttc"]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("CFont", fp, subfontIndex=0) if fp.endswith(".ttc") else TTFont("CFont", fp))
                return "CFont"
            except Exception:
                continue
    return None


def generate_contract(client_name, project_name, total_amount, contact="", phone="", email="", output_path=None):
    font_name = setup_chinese_font()
    if not font_name:
        print("❌ 中文字体注册失败")
        return None

    if output_path is None:
        safe = "".join(c for c in client_name if c.isalnum() or c in "_-")
        output_path = f"合同_{safe}_{datetime.now().strftime('%Y%m%d')}.pdf"

    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=2.2*cm, rightMargin=2.2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("T", parent=styles["Title"], fontName=font_name, fontSize=22, textColor=colors.HexColor("#0066ff"), alignment=TA_CENTER, spaceAfter=16)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName=font_name, fontSize=12, textColor=colors.HexColor("#0066ff"), spaceBefore=10, spaceAfter=6, leading=18)
    normal = ParagraphStyle("N", parent=styles["Normal"], fontName=font_name, fontSize=10, textColor=colors.HexColor("#374151"), leading=17)
    bold = ParagraphStyle("B", parent=normal, fontName=font_name, textColor=colors.HexColor("#1a1a2e"))

    elements.append(Paragraph("技 术 服 务 合 同", title_style))
    elements.append(Spacer(1, 0.3*cm))

    contract_no = f"FY-HT-{datetime.now().strftime('%Y%m%d')}"
    info = [
        ["合同编号", contract_no, "签订日期", "______ 年 ___ 月 ___ 日"],
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

    # 双方信息
    elements.append(Paragraph("甲方（委托方）", h2))
    a_data = [
        ["名称", client_name],
        ["联系人", contact or "____________________"],
        ["联系电话", phone or "____________________"],
        ["邮箱", email or "____________________"],
        ["地址", "____________________"],
    ]
    a_t = Table(a_data, colWidths=[3*cm, 14*cm])
    a_t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f8f9fa")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(a_t)
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph("乙方（受托方）", h2))
    b_data = [
        ["名称", "宝鸡丰悦云创科技有限公司"],
        ["法定代表人", "丰悦"],
        ["地址", "陕西省宝鸡市渭滨区高新开发区高新大道188号院5幢2层"],
        ["联系电话", "____________________"],
        ["邮箱", "3954591720@qq.com"],
    ]
    b_t = Table(b_data, colWidths=[3*cm, 14*cm])
    b_t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f8f9fa")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(b_t)
    elements.append(Spacer(1, 0.5*cm))

    # 鉴于
    elements.append(Paragraph("鉴于甲方拟委托乙方提供技术服务，经双方友好协商，依据《中华人民共和国民法典》及相关法律法规，达成如下协议：", normal))
    elements.append(Spacer(1, 0.3*cm))

    # 条款
    elements.append(Paragraph("一、服务内容", h2))
    elements.append(Paragraph(f"1.1 乙方为甲方提供以下技术服务：<b>{project_name}</b>", normal))
    elements.append(Paragraph(f"1.2 详细需求规格见附件一《需求规格说明书》。", normal))
    elements.append(Paragraph(f"1.3 详细技术方案见附件二《技术方案说明书》。", normal))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("二、服务期限", h2))
    elements.append(Paragraph("2.1 启动日期：合同签订且首付款到账后 3 个工作日内启动。", normal))
    elements.append(Paragraph("2.2 详细里程碑见附件三《项目进度表》。", normal))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("三、服务费用", h2))
    elements.append(Paragraph(f"3.1 本合同总金额为人民币 ¥{total_amount:,.0f} 元（大写：____________________元整），含税。", normal))
    elements.append(Paragraph("3.2 付款方式：", normal))
    if total_amount < 5000:
        pay_text = "合同签订后 3 日内支付全款。"
    elif total_amount < 50000:
        pay_text = f"50% 预付款 ¥{total_amount*0.5:,.0f} 元（合同签订后 3 日内）+ 50% 尾款 ¥{total_amount*0.5:,.0f} 元（验收合格后 7 日内）。"
    else:
        pay_text = f"30% 启动款 ¥{total_amount*0.3:,.0f} 元 + 40% 中期款 ¥{total_amount*0.4:,.0f} 元 + 30% 尾款 ¥{total_amount*0.3:,.0f} 元。"
    elements.append(Paragraph(f"  {pay_text}", normal))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("四、双方权利义务", h2))
    elements.append(Paragraph("4.1 甲方：按约定提供资料、配合人员、按时付款、及时验收。", normal))
    elements.append(Paragraph("4.2 乙方：按约定提供技术服务、定期汇报进度、提供验收材料及售后维护。", normal))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("五、知识产权", h2))
    elements.append(Paragraph("5.1 项目成果在甲方付清全款后归甲方所有；付清前归乙方所有。", normal))
    elements.append(Paragraph("5.2 第三方开源组件许可协议保持原状。", normal))
    elements.append(Paragraph("5.3 乙方保留脱敏后项目经验的展示权，甲方如不同意需书面声明。", normal))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("六、保密", h2))
    elements.append(Paragraph("双方对合作中知悉的对方商业秘密负有保密义务，保密期限：自合作终止之日起 3 年。", normal))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("七、违约责任", h2))
    elements.append(Paragraph("7.1 甲方逾期付款：每逾期一日按未付金额的 0.05% 支付违约金。", normal))
    elements.append(Paragraph("7.2 乙方逾期交付：每逾期一日按合同总金额的 0.05% 支付违约金（不可抗力除外）。", normal))
    elements.append(Paragraph("7.3 违反保密义务：支付合同总金额 30% 的违约金。", normal))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("八、不可抗力", h2))
    elements.append(Paragraph("因不可抗力（自然灾害、疫情、政策变化、第三方服务大规模中断等）导致无法履约的，应及时通知对方，提供证明，合理期限内提供替代方案。", normal))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("九、争议解决", h2))
    elements.append(Paragraph("本合同适用中华人民共和国法律。争议优先友好协商；协商不成的，提交宝鸡仲裁委员会仲裁。", normal))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("十、其他", h2))
    elements.append(Paragraph("本合同自双方签字盖章之日起生效，一式两份，双方各执一份，具同等法律效力。", normal))
    elements.append(Spacer(1, 1*cm))

    # 签字
    sign = [
        ["", ""],
        ["甲方（盖章）：", "乙方（盖章）："],
        [client_name, "宝鸡丰悦云创科技有限公司"],
        ["", ""],
        ["法定代表人/授权代表签字：", "法定代表人/授权代表签字："],
        ["____________________", "____________________"],
        ["", ""],
        ["日期：______ 年 ___ 月 ___ 日", "日期：______ 年 ___ 月 ___ 日"],
    ]
    s_t = Table(sign, colWidths=[8.5*cm, 8.5*cm], rowHeights=[0.3*cm, 0.6*cm, 0.6*cm, 0.3*cm, 0.6*cm, 0.8*cm, 0.3*cm, 0.6*cm])
    s_t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ]))
    elements.append(s_t)

    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph(
        "<para align='center'><font size=8 color='#9ca3af'>本模板仅供参考，签署前建议由专业律师审阅。</font></para>",
        normal
    ))

    doc.build(elements)
    return output_path


def main():
    if len(sys.argv) < 4:
        print("用法：python3 generate_contract.py <甲方公司名> <项目名> <总金额> [联系人] [联系电话] [邮箱]")
        print("")
        print("示例：")
        print('  python3 generate_contract.py "某教育公司" "智能客服系统" 28000')
        print('  python3 generate_contract.py "某餐饮品牌" "会员小程序" 18000 "张总" "13800001111" "zhang@example.com"')
        sys.exit(1)

    client = sys.argv[1]
    project = sys.argv[2]
    amount = float(sys.argv[3])
    contact = sys.argv[4] if len(sys.argv) > 4 else ""
    phone = sys.argv[5] if len(sys.argv) > 5 else ""
    email = sys.argv[6] if len(sys.argv) > 6 else ""

    path = generate_contract(client, project, amount, contact, phone, email)
    if path:
        abs_path = os.path.abspath(path)
        size = os.path.getsize(path)
        print(f"")
        print(f"✅ 合同 PDF 生成成功")
        print(f"📄 文件：{abs_path}")
        print(f"📦 大小：{size:,} 字节")


if __name__ == "__main__":
    main()