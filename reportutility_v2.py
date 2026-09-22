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
        'Lower Relative': 'Maintaining healthy routines, adequate sleep, relaxation practices, and supportive social connections is recommended. Awareness of situations that contribute to worry may also be helpful',
        'Mild Relative': 'Slow breathing, grounding exercises, structured routines, and identifying worry triggers are recommended. Psychoeducation and counselling support may also be considered if concerns persist',
        'Moderate Relative': 'Counselling support is recommended to explore the nature, frequency, and impact of anxiety. Coping strategies, relaxation practices, sleep regulation, and monitoring of symptoms are also recommended',
        'Higher Relative': 'Timely professional review is recommended to understand the intensity and functional impact of anxiety. An individualized support plan addressing coping skills, sleep, daily functioning, and stressors is recommended'
    },
    'Depression': {
        'Lower Relative': 'Meaningful activities, healthy routines, supportive relationships, and regular self-care are recommended.',
        'Mild Relative': 'Daily routines, appropriate physical activity, positive social engagement, enjoyable activities, and awareness of mood changes are recommended. Psychoeducation and counselling support may also be considered.',
        'Moderate Relative': 'Counselling support is recommended to explore mood, energy, concentration, interest in activities, and their impact on daily functioning. Structured activity planning and social support are also recommended.',
        'Higher Relative': 'Timely professional assessment and individualized support are recommended to explore persistent mood-related concerns and their impact on daily functioning. Counselling or referral may be considered based on professional review.'
    },
    'Suicidal Ideation': {
        'Lower Relative': 'Emotional support, healthy coping strategies, and awareness of available campus counselling resources are recommended. Well-being check-ins may also be helpful where appropriate.',

        'Mild Relative': ' A supportive counselling conversation is recommended to understand the context of reported thoughts, emotional distress, and available support resources. Help-seeking and monitoring are also recommended.',

        'Moderate Relative': 'Prompt professional review is recommended to explore the nature, frequency, context, and impact of suicidal thoughts. Safety and support needs should be assessed directly.',

        'Higher Relative': 'Urgent professional safety assessment and immediate follow-up are required. The appropriate response should be determined through direct assessment and institutional protocol.'
    },
    'Substance Abuse': {
        'Lower Relative': 'A confidential, non-judgmental counselling discussion is recommended to understand the nature, frequency, context, and functional impact of substance use. Psychoeducation on healthier coping strategies is also recommended.',
        'Mild Relative': 'Professional review and individualized support are recommended to explore patterns, triggers, consequences, and available referral options',
        'Moderate Relative':'Professional review and individualized support are recommended to explore patterns, triggers, consequences, and available referral options',
        'Higher Relative': 'Supportive guidance, motivational conversations, and referral to an appropriate qualified professional or de-addiction service are recommended where indicated'
    },
    'Self-Esteem Problems': {
        'Lower Relative': 'Self-awareness, recognition of strengths, healthy self-talk, and meaningful activities are recommended.',
        'Mild Relative': 'Identifying strengths, challenging negative self-judgments, setting realistic goals, and accepting constructive feedback are recommended.',
        'Moderate Relative': 'Counselling support is recommended to explore negative self-perceptions, self-comparison, confidence concerns, and their impact on functioning.',
        'Higher Relative': 'Individualized professional support is recommended to explore persistent self-worth concerns and negative self-beliefs. Gradual strength-building and supportive goal-setting are also recommended.'
    },
    'Interpersonal Problems': {
        'Lower Relative': 'Healthy relationships, open communication, mutual respect, and positive social activities are recommended.',
        'Mild Relative': 'Active listening, assertive communication, boundary-setting, and seeking supportive connections are recommended.',
        'Moderate Relative': 'Counselling support is recommended to explore relationship difficulties, loneliness, trust concerns, communication patterns, and their impact on well-being.',
        'Higher Relative': 'Individualized counselling support is recommended for persistent interpersonal concerns, social isolation, trust difficulties, or relationship-related distress.'
    },
    'Family Problems': {
        'Lower Relative': 'Open family communication, mutual understanding, supportive relationships, and healthy personal boundaries are recommended',
        'Mild Relative': 'Constructive communication, identifying manageable sources of family stress, and seeking support from trusted individuals are recommended.',
        'Moderate Relative': 'Counselling support is recommended to explore family stress, expectations, communication difficulties, and their impact on emotional well-being.',
        'Higher Relative': 'Individualized professional support is recommended to understand persistent family-related distress and identify safe, practical coping and support options. Family involvement may be considered when appropriate.'
    },
    'Academic Stress': {
        'Lower Relative': 'Effective study routines, realistic academic goals, balanced schedules, and healthy breaks are recommended.',
        'Mild Relative': 'Time management, prioritization, planned study sessions, short breaks, and academic clarification or support are recommended when required.',
        'Moderate Relative': 'Counselling support is recommended to explore workload, expectations, performance concerns, and time-management difficulties. A structured academic action plan is also recommended',
        'Higher Relative': 'Timely professional and academic support are recommended to understand the impact of academic stress. An individualized plan addressing workload, prioritization, expectations, and institutional resources is recommended.'
    },
    'Career Concerns': {
        'Lower Relative': 'Career exploration, awareness of interests and strengths, and gradual planning for future goals are recommended.',
        'Mild Relative': 'Exploring interests, gathering reliable information, identifying strengths, and discussing options with a career counsellor, mentor, or faculty member are recommended.',
        'Moderate Relative': 'Structured career guidance is recommended to explore uncertainty, decision-making difficulties, interests, abilities, and realistic options. Breaking decisions into manageable steps is also recommended',
        'Higher Relative': 'Timely individualized career counselling is recommended to explore persistent career-related distress, decision pressure, uncertainty, and impact on functioning. A structured career-planning support plan is also recommended.'
    }
}

class V2ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_font("helvetica", size=12)
        self.set_margins(15, 10, 15)
        
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
    icon_size = 4
    
    draw_icon(pdf, icon_file, x=x + padding_x, y=y + padding_y, size=icon_size)
    
    title_x = x + padding_x + icon_size + 2
    pdf.set_xy(title_x, y + padding_y)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(*TITLE_COLOR)
    pdf.cell(width - (title_x - x) - padding_x, icon_size, title, align="L")
    
    desc_y = y + padding_y + icon_size + 2
    pdf.set_xy(x + padding_x, desc_y)
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(*BODY_COLOR)
    pdf.multi_cell(width - (padding_x * 2), 5, description, align="L")

def render_gentle_everyday_suggestions_page(pdf):
    pdf.set_font("Arial", "B", 14)
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
        pdf.set_font("Arial", "", 9)
        h1 = pdf.get_multi_cell_height(card_w - 8, 5, item1[1])
        h2 = pdf.get_multi_cell_height(card_w - 8, 5, item2[1])
        content_h = max(h1, h2)
        card_h = 4 + 6 + 2 + content_h + 4
        card_h = max(card_h, 25) # Minimum height

        draw_suggestion_cell(pdf, 15, y_start, card_w, card_h, item1[0], item1[1], item1[2])
        draw_suggestion_cell(pdf, 15 + card_w, y_start, card_w, card_h, item2[0], item2[1], item2[2])
        
        y_start += card_h

    pdf.set_y(y_start + 10) # 10 padding after grid


def create_v2_report(filepath, student_name, course, year, institute, scores, bands, critical_flag, graph_path=None):
    validate_required_assets()

    pdf = V2ReportPDF()
    pdf.add_font("Arial", "", str(font_path("arial.ttf")))
    pdf.add_font("Arial", "B", str(font_path("arialbd.ttf")))
    pdf.add_font("SegoeSymbol", "", str(font_path("symbol.ttf")))
    pdf.set_fallback_fonts(["SegoeSymbol"])
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
    # pdf.set_font("Times", style="B", size=23)
    # pdf.cell(0, 10, "PSYCHOMETRIC ASSESSMENT REPORT", align="C", new_x="LMARGIN", new_y="NEXT")
    # Set text color to pure black (RGB: 0, 0, 0)
    pdf.set_text_color(0, 0, 0)
    
    # Make sure your font style is set (e.g., Times Italic)
    pdf.set_font("Times", style="B", size=23)
    
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
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "PREPARED FOR-", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "B", 12)
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
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(*GREEN_TEXT)
    #student_name.split()[0]
    pdf.cell(0, 10, f"Hello {student_name.split()[0]},", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.multi_cell(0, 6, "We're glad you took a few minutes for yourself to complete this assessment.\nThat's already a meaningful first step.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, "This report reflects your responses across nine areas of everyday student life. There's no right or wrong here, it's simply a snapshot to help you understand what's feeling heavy right now, and where things are already going well.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(*GREEN_TEXT)
    pdf.cell(0, 10, "The nine areas we looked at:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(50, 100, 150)
    domains = ["Anxiety", "Depression", "Suicidal Ideation", "Substance Abuse", "Self-Esteem Problems", "Interpersonal Problems", "Family Problems", "Academic Stress", "Career Concerns"]
    for d in domains:
        pdf.cell(10, 8, "-", align="R")
        pdf.cell(0, 8, d, new_x="LMARGIN", new_y="NEXT")

    # ---------------- PAGE 3 ----------------
    pdf.add_page()
    pdf.set_y(20)
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(*GREEN_TEXT)
    pdf.cell(0, 10, "Understanding This Assessment", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 12)
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
        pdf.set_font("Arial", "B", 10)
        h1 = pdf.get_multi_cell_height(col_w1, row_h_base, row[0])
        pdf.set_font("Arial", "", 10)
        h2 = pdf.get_multi_cell_height(col_w2, row_h_base, row[1])
        
        row_height = max(h1, h2) + 4
        
        # Check page break
        
        x_before = pdf.get_x()
        y_before = pdf.get_y()
        
        # Draw cells
        pdf.set_fill_color(*row[2])
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)
        
        # Draw background and text for column 1
        pdf.rect(x_before, y_before, col_w1, row_height, 'DF')
        pdf.set_xy(x_before, y_before + 2)
        pdf.multi_cell(col_w1, row_h_base, row[0], align="L")
        
        # Draw background and text for column 2
        pdf.set_fill_color(245, 245, 245)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        
        pdf.rect(x_before + col_w1, y_before, col_w2, row_height, 'DF')
        pdf.set_xy(x_before + col_w1 + 2, y_before + 2)
        pdf.multi_cell(col_w2 - 4, row_h_base, row[1], align="L")
        
        pdf.set_xy(x_before, y_before + row_height)

        # ---------------- PAGE 4 ----------------
    pdf.add_page()
    pdf.set_y(20)
    pdf.set_font("Arial", "B", 13.5)
    pdf.set_text_color(30, 95, 90) # #1e5f5a
    pdf.cell(0, 10, "Assessment Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Header
    pdf.set_fill_color(30, 95, 90)
    pdf.set_text_color(255, 255, 255)
    pdf.set_draw_color(199, 219, 217) # Light teal borders
    pdf.set_line_width(0.3)
    pdf.set_font("Arial", "B", 10)
    
    # Save x for tables
    start_x = pdf.get_x()
    
    pdf.cell(80, 8, " Domain", border=1, fill=True, align="L")
    pdf.cell(40, 8, "Score", border=1, fill=True, align="C")
    pdf.cell(60, 8, "Relative Band", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

    domain_names = ["Anxiety", "Depression", "Suicidal Ideation", "Substance Abuse", "Self-Esteem Problems", "Interpersonal Problems", "Family Problems", "Academic Stress", "Career Concerns"]

    higher_domains = []
    moderate_domains = []
    strength_domains = []
    
    # Helper to draw a thick red border around a specific row
    def draw_thick_red_border(y_pos):
        # Save state
        
        pdf.set_draw_color(225, 137, 85) # Orange border
        pdf.set_line_width(0.8)
        pdf.rect(start_x, y_pos, 180, 8, 'D')
        # Restore
        pdf.set_draw_color(199, 219, 217)
        pdf.set_line_width(0.3)

    for i, d in enumerate(domain_names):
        score = scores[i]
        band = bands[i]
        
        y_pos = pdf.get_y()
        is_higher = False

        if d == 'Substance Abuse':
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 10)
            pdf.cell(80, 8, f" {d}", border=1, fill=True)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 8, f"{score} / 24", border=1, fill=True, align="C")
            pdf.set_text_color(39, 174, 96)
            pdf.cell(60, 8, "Lower Relative", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
            strength_domains.append(d)
            continue

        if band == 'Higher Relative':
            higher_domains.append((d, score))
            pdf.set_fill_color(252, 239, 212) # #f9e6e6 Light red fill
            pdf.set_text_color(225, 137, 85) # Red text
            band_text = "Higher Relative"
            is_higher = True
        elif band == 'Moderate Relative':
            moderate_domains.append((d, score))
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(142, 68, 173)
            band_text = "Moderate Relative"
        elif band == 'Mild Relative':
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(41, 128, 185)
            band_text = "Mild Relative"
        else:
            if score == 0:
                strength_domains.append(d)
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(39, 174, 96)
            band_text = "Lower Relative"

        if is_higher:
            # Special rendering for higher relative row
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("SegoeSymbol", "", 10)
            pdf.cell(5, 8, u" ★", border="LBT", fill=True)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(75, 8, f" {d}", border="RBT", fill=True)
            pdf.cell(40, 8, f"{score} / 24", border=1, fill=True, align="C")
            pdf.set_text_color(225, 137, 85)
            pdf.cell(60, 8, band_text, border=1, fill=True, align="C")
            draw_thick_red_border(y_pos)
            pdf.ln(8)
        else:
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(80, 8, f" {d}", border=1, fill=True)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 8, f"{score} / 24", border=1, fill=True, align="C")
            
            if band == 'Moderate Relative':
                pdf.set_text_color(142, 68, 173)
            elif band == 'Mild Relative':
                pdf.set_text_color(41, 128, 185)
            else:
                pdf.set_text_color(39, 174, 96)
            pdf.cell(60, 8, band_text, border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)
    pdf.set_line_width(0.3)

    import os
    if graph_path and os.path.exists(graph_path):
        # Image w=170, h is auto-calculated but roughly 106.
        # We might need to check if it fits, but on A4 it should fit with table and safety box.
        y_before_graph = pdf.get_y()
        pdf.image(graph_path, x=20, w=170)
        # get_y() does not auto-update when using pdf.image directly unless it's in a flow, wait, FPDF pdf.image DOES NOT UPDATE get_y().
        # We must manually set_y after image.
        pdf.set_y(y_before_graph + 110)

    # SAFETY STATUS BOX
    # if critical_flag:
    #     pdf.set_fill_color(255, 230, 230)
    #     pdf.set_draw_color(*RED_TEXT)
    #     pdf.rect(15, pdf.get_y(), 180, 32, 'DF')
        
    #     pdf.set_xy(17, pdf.get_y() + 2)
    #     pdf.set_font("Arial", "B", 13.5)
    #     pdf.set_text_color(*RED_TEXT)
    #     pdf.cell(0, 8, "Safety Status", new_x="LMARGIN", new_y="NEXT")
        
    #     pdf.set_xy(17, pdf.get_y())
    #     pdf.set_font("Arial", "B", 11)
    #     pdf.cell(0, 6, "! CRITICAL SAFETY FLAG DETECTED", new_x="LMARGIN", new_y="NEXT")
        
    #     pdf.set_xy(17, pdf.get_y())
    #     pdf.set_font("Arial", "", 11)
    #     pdf.set_text_color(0, 0, 0)
    #     pdf.multi_cell(176, 5, "Please connect with a counselor immediately. One or more critical safety items were endorsed by the student.", align="L")
    # else:
    #     # Reference #eaf7f1 fill, #2e9985 border
    #     pdf.set_fill_color(234, 247, 241)
    #     pdf.set_draw_color(46, 153, 133)
    #     pdf.rect(15, pdf.get_y(), 180, 32, 'DF')
        
    #     pdf.set_xy(17, pdf.get_y() + 2)
    #     pdf.set_font("Arial", "B", 13.5)
    #     pdf.set_text_color(76, 195, 176) # #4cc3b0
    #     pdf.cell(0, 8, "Safety Status", new_x="LMARGIN", new_y="NEXT")
        
    #     pdf.set_xy(17, pdf.get_y())
    #     pdf.set_font("Arial", "B", 11)
    #     pdf.set_text_color(30, 95, 90) # #1e5f5a
        
    #     # Use ✓ character instead of v
    #     # We need to make sure python encodes this correctly
    #     pdf.set_font("SegoeSymbol", "", 11)
    #     pdf.cell(5, 6, u"✓", new_x="RIGHT", new_y="TOP")
    #     pdf.set_font("Arial", "B", 11)
    #     pdf.cell(0, 6, " No critical safety items were endorsed", new_x="LMARGIN", new_y="NEXT")
        
    #     pdf.set_xy(17, pdf.get_y())
    #     pdf.set_font("Arial", "", 11)
    #     pdf.set_text_color(0, 0, 0)
    #     pdf.multi_cell(176, 5, "The three designated critical safety items -- covering past attempts, a clear plan, or thoughts of obtaining means to end one's life -- were all rated 'Never' by the student.", align="L")

    pdf.set_y(pdf.get_y() + 10)

        # ---------------- PAGE 5 ----------------
    pdf.add_page()
    pdf.set_y(20)

    # 1. Where to Focus Support
    pdf.set_font("Arial", "B", 13.5)
    pdf.set_text_color(225, 137, 85)  # Title orange
    pdf.cell(0, 8, "Where to Focus Support", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(0, 0, 0)
    
    if len(higher_domains) > 0:
        num_str = "Two" if len(higher_domains) == 2 else ("One" if len(higher_domains) == 1 else str(len(higher_domains)))
        domain_plural = "domains fall" if len(higher_domains) > 1 else "domain falls"
        pdf.multi_cell(180, 5, f"{num_str} {domain_plural} in the Higher Relative range this cycle and are the natural starting points for a supportive check-in.")
        pdf.ln(4)
        
        first_name = student_name.split()[0] if student_name else "the student"
        FOCUS_SUPPORT_TEXTS = {
            "Academic Stress": "This suggests noticeable pressure around workload, deadlines, and matching effort to results, common and very manageable first-year experiences\n\nA conversation exploring study planning, time-management strategies, and realistic expectation-setting could offer quick, tangible relief.",
            "Family Problems": f"There is some indication of tension, high expectations, or communication gaps at home that {first_name} is carrying alongside academic life.\n\nGently exploring the support system and current home context is a good next step."
        }
        
        for d, s in higher_domains:
            desc = FOCUS_SUPPORT_TEXTS.get(d, f"This suggests noticeable pressure around {d.lower()}. A conversation exploring strategies and realistic expectation-setting could offer quick, tangible relief.")
            
            pdf.set_font("Arial", "", 11)
            h = pdf.get_multi_cell_height(176, 5, desc) + 14

            y_box = pdf.get_y()
            pdf.set_fill_color(252, 239, 212) # #fcefd4
            pdf.set_draw_color(232, 147, 91)  # #e8935b
            pdf.set_line_width(0.4)
            pdf.rect(15, y_box, 180, h, "DF")

            pdf.set_xy(17, y_box + 2)
            pdf.set_font("Arial", "B", 11)
            pdf.set_text_color(225, 137, 85)
            # Use ascii hyphen to avoid cp1252 issues, space it to look like em-dash
            pdf.cell(0, 7, f"{d} - {s}/24 (Higher Relative)", new_x="LMARGIN", new_y="NEXT")

            pdf.set_xy(17, pdf.get_y() + 1)
            pdf.set_font("Arial", "", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(176, 5, desc)
            pdf.set_y(y_box + h + 6)
            
    else:
        pdf.multi_cell(180, 5, "No domains fall in the Higher Relative range this cycle.")
        pdf.ln(8)

    # 2. Recommended Support Plan
    pdf.ln(2)
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(40, 100, 80)
    pdf.cell(0, 10, "Recommended Support Plan", new_x="LMARGIN", new_y="NEXT")
    
    # Generate bullet texts directly from RECOMMENDATIONS dictionary
    bullets = []
    
    # We will output recommendations for all domains based on their specific band
    domain_list = ['Anxiety', 'Depression', 'Suicidal Ideation', 'Substance Abuse', 'Self-Esteem Problems', 'Interpersonal Problems', 'Family Problems', 'Academic Stress', 'Career Concerns']
    
    for d, b in zip(domain_list, bands):
        # Substance abuse has special logic in bands sometimes ('Any reported concern' or 'None')
        # We need to map it back to the dictionary keys if it doesn't match
        if d == 'Substance Abuse':
            if b == 'Any reported concern':
                b = 'Higher Relative' # Fallback for dict mapping if needed
            elif b == 'None':
                b = 'Lower Relative'
                
        rec = RECOMMENDATIONS.get(d, {}).get(b, "")
        if rec:
            # bullets.append(f"{d}: {rec}")
            bullets.append(f"●  {rec}")
            
    # Draw Bullet Table
    pdf.set_draw_color(224, 238, 238) # Light blue/teal border
    pdf.set_line_width(0.3)
    
    x_start = 15
    pdf.set_x(x_start)
    
    pdf.line(x_start, pdf.get_y(), 195, pdf.get_y())
    
    for i, bullet in enumerate(bullets):
        # Check if we need a page break manually
        h = pdf.get_multi_cell_height(168, 6, bullet) + 8
        if pdf.get_y() + h > 270:
            pdf.add_page()
            pdf.set_y(20)
            pdf.line(x_start, pdf.get_y(), 195, pdf.get_y())
            
        y_before = pdf.get_y()
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(0, 0, 0)
        
        
        pdf.set_xy(x_start + 6, y_before + 4)
        pdf.cell(5, 6, chr(149))
        
        # We manually change the left margin to ensure the hanging indent
        original_lmargin = pdf.l_margin
        text_x = x_start + 13
        pdf.set_left_margin(text_x)
        pdf.set_xy(text_x, y_before + 4)
        
        # Render text block
        pdf.multi_cell(195 - text_x, 6, bullet)
        
        # Restore margin
        pdf.set_left_margin(original_lmargin)
        
        actual_y = max(y_before + h, pdf.get_y() + 4)
        pdf.set_y(actual_y)
        # Draw bottom separator line ONLY (no side borders)
        pdf.line(x_start, pdf.get_y(), 195, pdf.get_y())
        
    pdf.ln(10)
    
    # 3. Color Coding Legend
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(255, 0, 0)
    pdf.cell(0, 6, "Color Coding:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(pdf.get_y() - 1)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, "1. Orange - Higher Relative", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "2. Purple - Moderate Relative", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "3. Blue - Mild Relative", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "4. Green - Lower Relative", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)


    # ---------------- PAGE 6 ----------------
    pdf.add_page()
    render_gentle_everyday_suggestions_page(pdf)

    # Contact Info at bottom of Page 6
    pdf.set_y(pdf.get_y() + 10)
    pdf.set_font("Arial", "BI", 12)
    pdf.set_text_color(90, 107, 112)
    pdf.cell(0, 8, "Recommendations", new_x="LMARGIN", new_y="NEXT")

    # Push the rest to the bottom
    pdf.set_y(260)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 5, "For more information, contact us:", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", "B", 9.5)
    pdf.set_text_color(30, 95, 90)
    pdf.cell(0, 5, "acrocare@acropolis.in   .   9630990027", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(90, 107, 112)
    pdf.cell(0, 5, "Acropolis Group of Institutions, Indore", align="C", new_x="LMARGIN", new_y="NEXT")

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
        pdf.set_font("Arial", "", 16)
        pdf.cell(0, 10, "Enlightening Wisdom", align="C", new_x="LMARGIN", new_y="NEXT")
        
    pdf.set_y(170)
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(30, 80, 160)
    pdf.cell(0, 10, "Acropolis Group of Institutions", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Address- Bypass Road, Manglia Square, Manglia, Indore, Madhya Pradesh - 453771", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Contact- 0731-4730000, 4730001", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.output(filepath)
