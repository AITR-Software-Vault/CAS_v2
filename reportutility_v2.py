import os
import pathlib
from fpdf import FPDF

from pathutility import (
    image_path,
    icon_path,
    font_path,
    validate_required_assets,
)

def draw_icon(pdf, path, x, y, size=6):
    import os
    if not os.path.isfile(str(path)):
        raise FileNotFoundError(f"Missing report icon: {path}")
    pdf.image(str(path), x=x, y=y, w=size, h=size)


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

RECOMMENDATIONS = {
    'Anxiety': {
        'Lower Relative': 'Continue healthy routines, adequate sleep, relaxation practices, and supportive social connections. Encourage awareness of situations that contribute to worry.',
        'Mild Relative': 'Encourage slow breathing, grounding exercises, structured routines, and identification of worry triggers. Psychoeducation and optional counselling may be offered if concerns persist.',
        'Moderate Relative': 'Recommend a counsellor discussion to explore the nature, frequency, and impact of anxiety. Encourage coping strategies, relaxation practice, sleep regulation, and monitoring of symptoms.',
        'Higher Relative': 'Recommend timely professional review to understand the intensity and functional impact of anxiety. Develop an individualized support plan addressing coping skills, sleep, daily functioning, and stressors.'
    },
    'Depression': {
        'Lower Relative': 'Encourage meaningful activities, healthy routines, supportive relationships, and regular self-care.',
        'Mild Relative': 'Encourage daily routines, appropriate physical activity, positive social engagement, enjoyable activities, and awareness of mood changes. Offer psychoeducation and optional counselling.',
        'Moderate Relative': 'Recommend a counsellor discussion to explore mood, energy, concentration, interest in activities, and impact on daily functioning. Encourage structured activity planning and social support.',
        'Higher Relative': 'Recommend timely professional assessment and individualized support to explore persistent mood-related concerns and functional impact. Offer counselling or referral based on professional review.'
    },
    'Suicidal Ideation': {
        'Lower Relative': 'Encourage emotional support, healthy coping strategies, and awareness of available campus counselling resources. Maintain well-being check-ins where appropriate.',
        'Mild Relative': 'Recommend a supportive counsellor conversation to understand the context of reported thoughts, emotional distress, and available support resources. Encourage help-seeking and monitoring.',
        'Moderate Relative': 'Recommend prompt professional review to explore the nature, frequency, context, and impact of suicidal thoughts. Assess safety and support needs directly.',
        'Higher Relative': 'Recommend urgent professional safety assessment and immediate follow-up. The appropriate response should be determined through direct assessment and institutional protocol.'
    },
    'Substance Abuse': {
        'Any reported concern': 'Encourage a confidential, non-judgmental counsellor discussion to understand the nature, frequency, context, and functional impact of substance use. Provide psychoeducation on healthier coping strategies.',
        'Use affects functioning': 'Recommend professional review and individualized support to explore patterns, triggers, consequences, and available referral options.',
        'Student wants to reduce/stop': 'Offer supportive guidance, motivational conversations, and referral to an appropriate qualified professional or de-addiction service where indicated.'
    },
    'Self-Esteem Problems': {
        'Lower Relative': 'Encourage self-awareness, recognition of strengths, healthy self-talk, and meaningful activities.',
        'Mild Relative': 'Encourage identifying strengths, challenging negative self-judgments, setting realistic goals, and accepting constructive feedback.',
        'Moderate Relative': 'Recommend counselling support to explore negative self-perceptions, self-comparison, confidence concerns, and their impact on functioning.',
        'Higher Relative': 'Recommend individualized professional support to explore persistent self-worth concerns and negative self-beliefs. Encourage gradual strength-building and supportive goal-setting.'
    },
    'Interpersonal Problems': {
        'Lower Relative': 'Encourage healthy relationships, open communication, mutual respect, and positive social activities.',
        'Mild Relative': 'Encourage active listening, assertive communication, boundary-setting, and seeking supportive connections.',
        'Moderate Relative': 'Recommend a counsellor discussion to explore relationship difficulties, loneliness, trust concerns, communication patterns, and their impact on well-being.',
        'Higher Relative': 'Recommend individualized counselling support for persistent interpersonal concerns, social isolation, trust difficulties, or relationship-related distress.'
    },
    'Family Problems': {
        'Lower Relative': 'Encourage open family communication, mutual understanding, supportive relationships, and healthy personal boundaries.',
        'Mild Relative': 'Encourage constructive communication, identifying manageable sources of family stress, and seeking support from trusted individuals.',
        'Moderate Relative': 'Recommend a counsellor discussion to explore family stress, expectations, communication difficulties, and their impact on emotional well-being.',
        'Higher Relative': 'Recommend individualized professional support to understand persistent family-related distress and identify safe, practical coping and support options. Consider family involvement only when appropriate.'
    },
    'Academic Stress': {
        'Lower Relative': 'Encourage effective study routines, realistic academic goals, balanced schedules, and healthy breaks.',
        'Mild Relative': 'Encourage time management, prioritization, planned study sessions, short breaks, and academic clarification or support when required.',
        'Moderate Relative': 'Recommend a counsellor discussion to explore workload, expectations, performance concerns, and time-management difficulties. Encourage a structured academic action plan.',
        'Higher Relative': 'Recommend timely professional and academic support to understand the impact of academic stress. Develop an individualized plan addressing workload, prioritization, expectations, and institutional resources.'
    },
    'Career Concerns': {
        'Lower Relative': 'Encourage career exploration, awareness of interests and strengths, and gradual planning for future goals.',
        'Mild Relative': 'Encourage exploring interests, gathering reliable information, identifying strengths, and discussing options with a career counsellor, mentor, or faculty member.',
        'Moderate Relative': 'Recommend structured career guidance to explore uncertainty, decision-making difficulties, interests, abilities, and realistic options. Break decisions into manageable steps.',
        'Higher Relative': 'Recommend timely individualized career counselling to explore persistent career-related distress, decision pressure, uncertainty, and impact on functioning. Develop a structured career-planning support plan.'
    }
}

class V2ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_font("helvetica", size=12)
        
    def get_multi_cell_height(self, w, h, txt, align='L'):
        lines = self.multi_cell(w, h, txt, align=align, dry_run=True, output="LINES")
        return len(lines) * h


def draw_suggestion_cell(pdf, x, y, width, height, title, description, icon_file):
    CELL_FILL = (246, 250, 250)
    CELL_BORDER = (205, 225, 225)
    TITLE_COLOR = (20, 65, 65)
    BODY_COLOR = (45, 62, 72)
    
    pdf.set_fill_color(*CELL_FILL)
    pdf.set_draw_color(*CELL_BORDER)
    pdf.set_line_width(0.3)
    pdf.rect(x, y, width, height, 'DF')
    
    padding_x = 4
    padding_y = 4
    icon_size = 6
    
    draw_icon(pdf, icon_file, x=x + padding_x, y=y + padding_y, size=icon_size)
    
    title_x = x + padding_x + icon_size + 2
    pdf.set_xy(title_x, y + padding_y)
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(*TITLE_COLOR)
    pdf.cell(width - (title_x - x) - padding_x, icon_size, title, align="L")
    
    desc_y = y + padding_y + icon_size + 2
    pdf.set_xy(x + padding_x, desc_y)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(*BODY_COLOR)
    pdf.multi_cell(width - (padding_x * 2), 5, description, align="L")

def render_gentle_everyday_suggestions_page(pdf):
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(62, 190, 180)
    pdf.cell(0, 10, "Gentle Everyday Suggestions", new_x="LMARGIN", new_y="NEXT")

    suggestions = [
        ("Protect sleep", "Aim for 6-8 hours a night - sleep is one of the fastest levers for mood and focus.", str(icon_path("sleep.png"))),
        ("Move daily", "Even a 30-minute walk, good food and enough water can noticeably steady energy and stress.", str(icon_path("movement.png"))),
        ("Lean on people", "Regular time with family or friends who feel supportive can ease the load of a demanding term.", str(icon_path("people.png"))),
        ("Plan the workload", "Breaking deadlines into smaller steps can shrink that overwhelmed feeling around exams.", str(icon_path("workload.png"))),
        ("Talk it through", "A short conversation with a counselor can help turn career uncertainty into a clearer next step.", str(icon_path("conversation.png"))),
        ("Reach out early", "Support is most useful before pressure builds - checking in now is a strength, not a setback.", str(icon_path("reach_out.png")))
    ]

    usable_width = 180
    card_w = usable_width / 2
    y_start = pdf.get_y() + 2

    for i in range(3):
        item1 = suggestions[i*2]
        item2 = suggestions[i*2+1]
        
        # Calculate dynamic height
        pdf.set_font("DejaVu", "", 9)
        h1 = pdf.get_multi_cell_height(card_w - 8, 5, item1[1])
        h2 = pdf.get_multi_cell_height(card_w - 8, 5, item2[1])
        content_h = max(h1, h2)
        card_h = 4 + 6 + 2 + content_h + 4
        card_h = max(card_h, 25) # Minimum height

        draw_suggestion_cell(pdf, 15, y_start, card_w, card_h, item1[0], item1[1], item1[2])
        draw_suggestion_cell(pdf, 15 + card_w, y_start, card_w, card_h, item2[0], item2[1], item2[2])
        
        y_start += card_h

    pdf.set_y(y_start + 10) # 10 padding after grid


def create_v2_report(filepath, student_name, course, year, institute, scores, bands, critical_flag):
    validate_required_assets()

    pdf = V2ReportPDF()
    pdf.add_font("DejaVu", "", str(font_path("DejaVuSans.ttf")))
    pdf.add_font("DejaVu", "B", str(font_path("DejaVuSans-Bold.ttf")))
    pdf.set_auto_page_break(auto=False)
    
    # colors
    GREEN_BG = hex_to_rgb('#E8F4EC')
    GREEN_TEXT = hex_to_rgb('#2E7D32')
    RED_TEXT = hex_to_rgb('#C62828')
    ORANGE_TEXT = hex_to_rgb('#E65100')
    
    # ---------------- PAGE 1 ----------------
    pdf.add_page()
    logo_path = str(image_path('acropolis_logo_transparent.png'))
    if True: # Handled by validate_required_assets
        pdf.image(logo_path, x=65, y=50, w=80)
    
    pdf.set_y(150)
    pdf.text_mode = "FILL"
    # pdf.set_text_color(0, 0, 0)
    # # pdf.set_font("Times", "I", 20)
    # pdf.set_font("Times", style="I", size=14)
    # pdf.cell(0, 10, "PSYCHOMETRIC ASSESSMENT REPORT", align="C", new_x="LMARGIN", new_y="NEXT")
    # Set text color to pure black (RGB: 0, 0, 0)
    pdf.set_text_color(0, 0, 0)
    
    # Make sure your font style is set (e.g., Times Italic)
    pdf.set_font("Times", style="I", size=14)
    
    # Print your cell
    pdf.cell(
        0,
        10,
        "PSYCHOMETRIC ASSESSMENT REPORT",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(0, 15, "2026-27", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_y(250)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, "PREPARED FOR-", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "B", 12)
    footer_text = f"{student_name} | {course} | {year} | {institute}"
    pdf.cell(0, 10, footer_text, align="C", new_x="LMARGIN", new_y="NEXT")
    
    # ---------------- PAGE 2 ----------------
    pdf.add_page()
    pdf.set_fill_color(*GREEN_BG)
    pdf.rect(0, 0, 210, 297, 'F')
    
    illus1 = str(image_path('intro_illustration_1.png'))
    if True:
        pdf.image(illus1, x=130, y=20, w=60)
        
    illus2 = str(image_path('intro_illustration_2.png'))
    if True:
        pdf.image(illus2, x=20, y=200, w=60)
        
    pdf.set_y(60)
    pdf.set_font("DejaVu", "B", 18)
    pdf.set_text_color(*GREEN_TEXT)
    pdf.cell(0, 10, f"Hello {student_name},", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_font("DejaVu", "B", 12)
    pdf.multi_cell(0, 6, "We're glad you took a few minutes for yourself to complete this assessment.\nThat's already a meaningful first step.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("DejaVu", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, "This report reflects your responses across nine areas of everyday student life. There's no right or wrong here, it's simply a snapshot to help you understand what's feeling heavy right now, and where things are already going well.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("DejaVu", "B", 12)
    pdf.set_text_color(*GREEN_TEXT)
    pdf.cell(0, 10, "The nine areas we looked at:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("DejaVu", "B", 12)
    pdf.set_text_color(50, 100, 150)
    domains = ["Anxiety", "Depression", "Suicidal Ideation", "Substance Abuse", "Self-Esteem Problems", "Interpersonal Problems", "Family Problems", "Academic Stress", "Career Concerns"]
    for d in domains:
        pdf.cell(10, 8, "-", align="R")
        pdf.cell(0, 8, d, new_x="LMARGIN", new_y="NEXT")

    # ---------------- PAGE 3 ----------------
    pdf.add_page()
    pdf.set_y(20)
    pdf.set_font("DejaVu", "B", 18)
    pdf.set_text_color(*GREEN_TEXT)
    pdf.cell(0, 10, "Understanding This Assessment", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, "This assessment looks at nine areas of a student's day-to-day experience over the past two weeks. Together they build a rounded picture of wellbeing, not a label, but a starting point for a supportive conversation.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Table of domains
    col_w1 = 55
    col_w2 = 135
    row_h_base = 6
    
    table_data = [
        ("Anxiety", "The body's natural early-warning response to stress -- worry, tension, restlessness and racing thoughts.", (220, 80, 80)),
        ("Depression", "Persistent low mood, reduced enjoyment, fatigue or difficulty concentrating that can affect daily functioning.", (120, 180, 100)),
        ("Suicidal Ideation", "Thoughts, ideas or ruminations about ending one's life. Any endorsement here is reviewed with the highest priority.", (150, 100, 180)),
        ("Substance Abuse", "A pattern of using alcohol, tobacco or other substances that causes distress or interferes with daily life.", (80, 150, 180)),
        ("Self-Esteem Problems", "How a person feels about their own worth, abilities and limitations.", (220, 150, 80)),
        ("Interpersonal Problems", "Disagreement or difficulty in relationships -- emotional, social or professional.", (200, 80, 80)),
        ("Family Problems", "Dynamics, behaviors or patterns at home that create tension for the student.", (120, 180, 100)),
        ("Academic Stress", "Confusion, time-pressure or disengagement connected to coursework and performance.", (150, 100, 180)),
        ("Career Concerns", "Uncertainty, indecision or pressure related to future career choices.", (80, 150, 180)),
    ]
    
    for row in table_data:
        # Calculate heights
        pdf.set_font("DejaVu", "B", 10)
        h1 = pdf.get_multi_cell_height(col_w1, row_h_base, row[0])
        pdf.set_font("DejaVu", "", 10)
        h2 = pdf.get_multi_cell_height(col_w2, row_h_base, row[1])
        
        row_height = max(h1, h2) + 4
        
        # Check page break
        
        x_before = pdf.get_x()
        y_before = pdf.get_y()
        
        # Draw cells
        pdf.set_fill_color(*row[2])
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("DejaVu", "B", 10)
        
        # Draw background and text for column 1
        pdf.rect(x_before, y_before, col_w1, row_height, 'DF')
        pdf.set_xy(x_before, y_before + 2)
        pdf.multi_cell(col_w1, row_h_base, row[0], align="L")
        
        # Draw background and text for column 2
        pdf.set_fill_color(245, 245, 245)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVu", "", 10)
        
        pdf.rect(x_before + col_w1, y_before, col_w2, row_height, 'DF')
        pdf.set_xy(x_before + col_w1 + 2, y_before + 2)
        pdf.multi_cell(col_w2 - 4, row_h_base, row[1], align="L")
        
        pdf.set_xy(x_before, y_before + row_height)

    # ---------------- PAGE 4 ----------------
    pdf.add_page()
    pdf.set_y(20)
    pdf.set_font("DejaVu", "B", 16)
    pdf.set_text_color(*GREEN_TEXT)
    pdf.cell(0, 10, "Assessment Summary & Safety", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_fill_color(30, 80, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(80, 10, "Domain", border=1, fill=True, align="L")
    pdf.cell(40, 10, "Score", border=1, fill=True, align="C")
    pdf.cell(70, 10, "Relative Band", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_text_color(0, 0, 0)
    domain_names = ["Anxiety", "Depression", "Suicidal Ideation", "Substance Abuse", "Self-Esteem Problems", "Interpersonal Problems", "Family Problems", "Academic Stress", "Career Concerns"]
    
    higher_domains = []
    moderate_domains = []
    strength_domains = []
    
    for i, d in enumerate(domain_names):
        score = scores[i]
        band = bands[i]
        
        if d == 'Substance Abuse':
            band_text = "Any concern" if score > 0 else "None"
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(*(ORANGE_TEXT if score > 0 else GREEN_TEXT))
            pdf.set_font("DejaVu", "", 10)
            pdf.cell(80, 10, d, border=1, fill=False)
            pdf.cell(40, 10, f"{score} / 24", border=1, fill=False, align="C")
            pdf.cell(70, 10, "Not banded", border=1, fill=False, align="C", new_x="LMARGIN", new_y="NEXT")
            if score > 0:
                moderate_domains.append((d, score)) # put in moderate list for recommendations
            continue

        if band == 'Higher Relative':
            higher_domains.append((d, score))
            pdf.set_fill_color(255, 230, 230)
            pdf.set_text_color(*RED_TEXT)
            prefix = "* "
            band_text = "Higher Relative"
            band = "Higher"
        elif band == 'Moderate Relative':
            moderate_domains.append((d, score))
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(*ORANGE_TEXT)
            prefix = ""
            band_text = "Moderate Relative"
        elif band == 'Mild Relative':
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(*GREEN_TEXT)
            prefix = ""
            band_text = "Mild Relative"
        else:
            if score == 0:
                strength_domains.append(d)
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(*GREEN_TEXT)
            prefix = ""
            band_text = "Lower Relative"
            
        pdf.set_font("DejaVu", "B" if band == 'Higher' else "", 10)
        pdf.cell(80, 10, prefix + d, border=1, fill=(band=='Higher'))
        pdf.cell(40, 10, f"{score} / 24", border=1, fill=(band=='Higher'), align="C")
        pdf.cell(70, 10, band_text, border=1, fill=(band=='Higher'), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(60, 180, 160)
    pdf.cell(0, 10, "Safety Status", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_fill_color(*GREEN_BG)
    pdf.set_draw_color(*GREEN_TEXT)
    pdf.set_line_width(0.5)
    
    if critical_flag:
        pdf.set_fill_color(255, 230, 230)
        pdf.set_draw_color(*RED_TEXT)
        pdf.set_text_color(*RED_TEXT)
        pdf.cell(0, 10, " CRITICAL SAFETY FLAG DETECTED.", border="LTR", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 8, "Please connect with a counselor immediately.\nOne or more critical safety items were endorsed by the student.", border="LBR", fill=True, new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_text_color(*GREEN_TEXT)
        pdf.cell(0, 10, " [OK] No critical safety items were endorsed", border="LTR", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, "The three designated critical safety items -- covering past attempts, a clear plan, or thoughts of obtaining means to end one's life -- were all rated \"Never\" by the student.", border="LBR", fill=True, new_x="LMARGIN", new_y="NEXT")
        
    pdf.set_line_width(0.2)
    pdf.set_draw_color(0, 0, 0)

    # ---------------- PAGE 5 ----------------
    pdf.add_page()
    pdf.set_y(20)
    pdf.set_font("DejaVu", "B", 18)
    pdf.set_text_color(*GREEN_TEXT)
    pdf.cell(0, 10, "Domain & Strength Analysis", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(*ORANGE_TEXT)
    pdf.cell(0, 10, "Where to Focus Support", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(0, 0, 0)
    
    if len(higher_domains) > 0:
        pdf.multi_cell(0, 6, f"{len(higher_domains)} domain(s) fall in the Higher Relative range this cycle and are the natural starting points for a supportive check-in.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.set_fill_color(255, 240, 230)
        pdf.set_draw_color(*ORANGE_TEXT)
        pdf.set_line_width(0.5)
        
        for d, s in higher_domains:
            # Check page break
            pdf.set_font("DejaVu", "B", 11)
            pdf.set_text_color(*ORANGE_TEXT)
            pdf.cell(0, 10, f" {d} -- {s}/24 (Higher Relative)", border="LTR", fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("DejaVu", "", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, f"This suggests noticeable pressure around {d.lower()}. A conversation exploring strategies and realistic expectation-setting could offer quick, tangible relief.", border="LBR", fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)
    else:
        pdf.multi_cell(0, 6, "No domains fall in the Higher Relative range this cycle.", new_x="LMARGIN", new_y="NEXT")

    pdf.set_line_width(0.2)
    pdf.set_draw_color(0, 0, 0)
    
    if len(moderate_domains) > 0:
        pdf.ln(5)
        pdf.set_font("DejaVu", "B", 14)
        pdf.set_text_color(60, 130, 180)
        pdf.cell(0, 10, "Moderate Relative Domain", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_fill_color(240, 248, 255)
        pdf.set_draw_color(60, 130, 180)
        pdf.set_line_width(0.5)
        
        pdf.set_font("DejaVu", "B", 11)
        pdf.cell(0, 10, " Moderate Relative domains", border="LTR", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 11)
        pdf.set_text_color(0, 0, 0)
        
        mod_str = ", ".join([f"{d} ({s}/24)" for d, s in moderate_domains])
        pdf.multi_cell(0, 6, f"{mod_str} all fall in the Moderate Relative range.", border="LBR", fill=True, new_x="LMARGIN", new_y="NEXT")
        
    if len(strength_domains) > 0:
        pdf.ln(5)
        pdf.set_font("DejaVu", "B", 14)
        pdf.set_text_color(*GREEN_TEXT)
        pdf.cell(0, 10, "Areas of relative strength", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_fill_color(*GREEN_BG)
        pdf.set_draw_color(*GREEN_TEXT)
        
        str_domains = ", ".join([f"{d} (0/24)" for d in strength_domains])
        pdf.set_font("DejaVu", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"{str_domains} shows no endorsement at all.\nThese are encouraging signs -- the student appears to be maintaining connection and does not report these as a coping strategy.", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_line_width(0.2)
    pdf.set_draw_color(0, 0, 0)
    
    pdf.ln(5)
        
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(40, 100, 80)
    pdf.cell(0, 10, "Recommended Support Plan", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_fill_color(30, 80, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(40, 10, "Priority", border=1, fill=True, align="L")
    pdf.cell(150, 10, "Recommended Direction", border=1, fill=True, align="L", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("DejaVu", "", 10)
    
    def draw_support_row(priority, text, color):
        pdf.set_font("DejaVu", "", 10)
        h = pdf.get_multi_cell_height(150, 6, text) + 4
        
        x_before = pdf.get_x()
        y_before = pdf.get_y()
        
        pdf.set_text_color(*color)
        pdf.set_font("DejaVu", "B", 10)
        pdf.rect(x_before, y_before, 40, h, 'D')
        pdf.set_xy(x_before + 2, y_before + 2)
        pdf.cell(36, 6, priority, align="L")
        
        pdf.set_xy(x_before + 40, y_before)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVu", "", 10)
        pdf.rect(x_before + 40, y_before, 150, h, 'D')
        pdf.set_xy(x_before + 42, y_before + 2)
        pdf.multi_cell(146, 6, text, align="L")
        pdf.set_xy(x_before, y_before + h)

    for d, s in higher_domains:
        draw_support_row("High", f"{d}-focused check-in: understand current expectations and available support.", RED_TEXT)
        
    for d, s in moderate_domains:
        draw_support_row("Moderate", f"Explore {d.lower()} in relation to adjustment and coping strategies already in use.", ORANGE_TEXT)
        
    draw_support_row("Ongoing", "Build on existing strengths and identify further protective factors and goals.", (40, 140, 100))

    # ---------------- PAGE 6 ----------------
    pdf.add_page()
    render_gentle_everyday_suggestions_page(pdf)
    
    # ---------------- DYNAMIC RECOMMENDATIONS ----------------

    if pdf.get_y() > 250:
        pdf.add_page()
        
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(45, 62, 72)
    pdf.cell(0, 10, "Recommendations", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
        

    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(0, 0, 0)

    if critical_flag:
        pdf.set_font("DejaVu", "B", 11)
        pdf.set_text_color(*RED_TEXT)
        pdf.cell(0, 8, "Immediate Action Required (Critical Safety Flag)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, "A critical safety item was endorsed. It is highly recommended to connect with a counsellor immediately for a safety assessment and appropriate support planning. Do not rely solely on these suggestions.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    domains_to_recommend = []
    # Add Higher
    for d, s in higher_domains:
        domains_to_recommend.append((d, "Higher"))
    # Add Moderate
    for d, s in moderate_domains:
        domains_to_recommend.append((d, "Moderate"))

    if scores[3] > 0 and ('Substance Abuse', 'Higher') not in domains_to_recommend and ('Substance Abuse', 'Moderate') not in domains_to_recommend:
        domains_to_recommend.append(('Substance Abuse', 'Any reported concern'))

    if not domains_to_recommend:
        pdf.multi_cell(0, 6, "No specific areas of concern were identified. Continue to utilize healthy coping strategies and reach out if you feel overwhelmed in the future.", new_x="LMARGIN", new_y="NEXT")
    else:
        for d, band in domains_to_recommend:
            if pdf.get_y() > 260:
                pdf.add_page()
                
            if d == 'Substance Abuse':
                pdf.set_font("DejaVu", "B", 10)
                pdf.set_text_color(60, 100, 140)
                pdf.cell(0, 8, f"{d}", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("DejaVu", "", 10)
                pdf.set_text_color(0, 0, 0)
                rec_text = RECOMMENDATIONS.get(d, {}).get("Any reported concern", "")
                pdf.multi_cell(0, 6, rec_text, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(2)
                continue

            pdf.set_font("DejaVu", "B", 10)
            pdf.set_text_color(60, 100, 140)
            pdf.cell(0, 8, f"{d} ({band} Relative)", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("DejaVu", "", 10)
            pdf.set_text_color(0, 0, 0)
            rec_text = RECOMMENDATIONS.get(d, {}).get(f"{band} Relative", f"Consider seeking support for {d.lower()}.")
            pdf.multi_cell(0, 6, rec_text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

    if strength_domains:
        if pdf.get_y() > 260:
            pdf.add_page()
        pdf.set_font("DejaVu", "B", 10)
        pdf.set_text_color(*GREEN_TEXT)
        pdf.cell(0, 8, "Ongoing Strengths", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"The student shows relative strength in: {', '.join(strength_domains)}. Continue to build on these protective factors and utilize them as resources during stressful periods.", new_x="LMARGIN", new_y="NEXT")

    # Footer section on page 6 (if space permits, else page 7, but it belongs on page 6 typically)
    # The requirement says exactly 7 pages. So we must fit it on page 6.
    pdf.set_y(270)
        
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(80, 100, 100)
    pdf.cell(0, 6, "For more information, contact us:", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(20, 100, 100)
    pdf.cell(0, 6, "acrocare@acropolis.in  |  9630990027", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Acropolis Group of Institutions, Indore", align="C", new_x="LMARGIN", new_y="NEXT")

    # ---------------- PAGE 7 ----------------
    if pdf.page_no() < 7:
        pdf.add_page()
    
    # Check if there is enough space on page 7, else it flows to 8, but we try to keep it on 7
    if pdf.get_y() > 200:
        pdf.add_page()
    
    pdf.set_y(pdf.get_y() + 20 if pdf.get_y() > 100 else 100)
    logo_footer = str(image_path('footer_logo_transparent.png'))
    if True: # Handled by validate_required_assets
        pdf.image(logo_footer, x=30, y=100, w=150)
    else:
        pdf.set_font("times", "I", 20)
        pdf.set_text_color(40, 60, 120)
        pdf.cell(0, 10, "ACROPOLIS", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 16)
        pdf.cell(0, 10, "Enlightening Wisdom", align="C", new_x="LMARGIN", new_y="NEXT")
        
    pdf.set_y(170)
    pdf.set_font("DejaVu", "B", 16)
    pdf.set_text_color(30, 80, 160)
    pdf.cell(0, 10, "Acropolis Group of Institutions", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Address- Bypass Road, Manglia Square, Manglia, Indore, Madhya Pradesh - 453771", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Contact- 0731-4730000, 4730001", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.output(filepath)

