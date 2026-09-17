import config
import departmentdata as college
import recommendations as reco
from dirutility import clean_up

import heapq
import pathlib
import random
import string
import sqlite3
import os
import collections as coll
import openpyxl as op
from fpdf import FPDF

from typing import List


# Module's private variable 
__VOWELS      = ('a', 'e', 'i', 'o', 'u')
__CONSONANTS  = tuple(set(string.ascii_lowercase) - set(__VOWELS))

__DEF_FSIZE   = 12
__PG_WIDTH    = 210 #mm
__PG_HEIGHT   = 297 #mm
# __GRAPHS_DIR  = './temp'
__GRAPHS_DIR  = config.TEMPDIR
__IMGDIR  = './images'
__IMGS    = ('report-newpage-1.png', 'report-newpage-2.png', 'report-newpage-3.png',
        'report-newpage-4.png', 'report-newpage-5.png', 'report-newpage-6.png')

TEMPLATE_WITH_CONTACT   = 'template-with-contact-info.png'
ACROCARE_EMAIL          = r'mailto:acrocare@acropolis.in'
AITR_URL = r'https://aitr.ac.in/'
AITRGOOGLE_URL = r'https://www.google.com/search?q=acropolis+institute+of+technology+and+research&source=lmns&bih=568&biw=1366&hl=en&sa=X&ved=2ahUKEwi-7LL_oJD3AhWz_DgGHaamCjEQ_AUoAHoECAEQAA'
debug_setting = config.DEBUG_MODE

# def generate_codename(studata: list, department: str, count: int) -> str:
# def generate_codename(studata: list, department: str) -> str:
def generate_codename(studata: list) -> str:
    """ 
    Return a string in format: 
    <4-char-Department-code><2-char-Year><2-char-Name-initials>
    """

    # deptcode        = college.DEPT_CODE_MAP[department]
    department      = studata[-3]
    deptcode        = college.DEPT_CODE_MAP.get(department, department)
    stuname         = studata[0]
    nameinitials    = ''.join(word[0] for word in stuname.strip().split())
    yearstr         = studata[-2].strip()
    year : int      = 1 # default
    for i in yearstr.split():
        try:
            year    = int(i)
            break
        except ValueError:
            continue

    # nomenclature_str = f"{deptcode}{year}{nameinitials}{count:03}"
    nomenclature_str = f"{deptcode.upper()}{year:02}{nameinitials.upper()}"
    return nomenclature_str


# def generate_codenames_list(data: List[List[str]], whichdepartment: str) -> list:
def generate_codenames_list(data: List[List[str]]) -> list:
    codenames = []
    created_codenames = set()
    print(f'{data=}')
    # for gi, arr in enumerate(data, start=1):
    for gi in range(1, len(data)):
        # codename = ''
        count = 1
        # codename = generate_codename(data[gi], whichdepartment)
        print("index=",gi, end=" ")
        codename = generate_codename(data[gi])
        while (f'{codename}{count:03}' in created_codenames):
            count += 1
        codename = f'{codename}{count:03}'
        codenames.append(codename)
        created_codenames.add(codename)
    return codenames


def generate_codename_e1(name: str, lenlimit: int = None) -> str:
    codename = []
    for c in reversed(name):
        codename.extend( (c.lower(), random.choice(__VOWELS), random.choice(__CONSONANTS)) )
    return ''.join(codename)[:lenlimit].capitalize()


# Unused and deprecated function
def generate_codenames_list_e1(data: list):
    codenames = []
    for i in range(1, len(data)):
        name = data[i][0]
        guardian_name = data[i][2]
        requiredlen = 8
        name = name.split(' ')[0]
        guardian_name = guardian_name.split(' ')[0]
        codename = generate_codename(name, requiredlen)
        if (len(codename) < requiredlen):
            codename = generate_codename(guardian_name+name, requiredlen)
        codenames.append(codename)
    return codenames


def getsummaryname(survey_name: str) -> str:
    if (survey_name.strip() != ''):
        return f"Summary - {survey_name}.xlsx"
    return f"Summary.xlsx"


def Create_Summary(dirpath: str, tscores: list, 
                    studata: list, codenames: list, AllQuestions: list, Raw_scores: list,survey_name: str='', version: str='v1', scoring_results: list = None):
    score_headers = ('AN-TSCORE', 'DP-TSCORE', 'SI-TSCORE', 'SA-TSCORE', 'SE-TSCORE', 'IP-TSCORE', 'FP-TSCORE', 'AP-TSCORE', 'CP-TSCORE')
    if version == 'v2':
        score_headers = ('AN-Band', 'DP-Band', 'SI-Band', 'SA-Band', 'SE-Band', 'IP-Band', 'FP-Band', 'AS-Band', 'CC-Band', 'COMBINED')

    header = ('NAME', 
    'CODE NAME',
    # 'DEMOGRAPHICS (AGE, GENDER, INSTITUTE, STREAM, YEAR, MONTHY FAMILY INCOME)',
    # 'CONTACT DETAILS (EMAIL, MOBILE)',
    *studata[0][1:],
    *AllQuestions[0][0:],
    *Raw_scores[0][0:],
    *score_headers)
    wb = op.Workbook()
    sheet = wb.active
    sheet.append(header)
    for gi, cname in enumerate(codenames, start=1):
        name    = studata[gi][0]
        if version == 'v2' and scoring_results:
            sr = scoring_results[gi - 1]
            bands = [sr["domain_bands"][d] for d in ['Anxiety', 'Depression', 'Suicidal Ideation', 'Substance Abuse', 'Self-Esteem Problems', 'Interpersonal Problems', 'Family Problems', 'Academic Stress', 'Career Concerns']]
            scores = [sr["domain_scores"][d] for d in ['Anxiety', 'Depression', 'Suicidal Ideation', 'Substance Abuse', 'Self-Esteem Problems', 'Interpersonal Problems', 'Family Problems', 'Academic Stress', 'Career Concerns']]
            combined_score = sum(scores)
            sheet.append((name, cname, *studata[gi][1:], *AllQuestions[gi][0:], *scores, *bands, combined_score))
        else:
            sheet.append((name, cname, *studata[gi][1:], *AllQuestions[gi][0:], *Raw_scores[gi][0:], *tscores[gi]))

    wb.save(f"{dirpath}/{getsummaryname(survey_name)}")
    # if (survey_name.strip() != ''):
    #     survey_name = f" - {survey_name}"
    # wb.save(f"{dirpath}/Summary{survey_name}.xlsx")

def plot_scores_v2(pdfobj, col1: list, col2: list, 
                topproblemareas: list, combined_score: int):
    M = 8
    LIGHTBLUE = (224, 235, 255)
    pdfobj.ln(40)
    pdfobj.set_left_margin(M)
    pdfobj.set_right_margin(M)
    pdfobj.set_fill_color(*LIGHTBLUE)

    # Header Row
    pdfobj.cell(80,9, txt=col1[0], align='C', border=1)
    pdfobj.cell(60,9, txt='Score', align='C', border=1)
    pdfobj.cell(0,9, txt='Band', align='C', border=1)
    pdfobj.ln()

    fill = True
    domain_codes = ['AN', 'DP', 'SI', 'SA', 'SE', 'IP', 'FP', 'AS', 'CC']
    for j, (category, score) in enumerate(zip(col1[1:], col2[1:])):
        if (category in topproblemareas):
            fill = True
            pdfobj.set_font(style="B")
            pdfobj.set_fill_color(171, 107, 39)
            pdfobj.set_text_color(255)
        else:
            pdfobj.set_font(style="")
            pdfobj.set_fill_color(*LIGHTBLUE)
            pdfobj.set_text_color(0)

        band = get_band_v2(domain_codes[j], score)
        if category.startswith("Substance Abuse"):
            band = "N/A"
            
        pdfobj.cell(80,8, txt=category, border=1, fill=fill)
        pdfobj.cell(60,8, txt=str(score), align='C', border=1, fill=fill)
        pdfobj.cell(0,8, txt=band, align='C', border=1, fill=fill)
        pdfobj.ln()
        fill = not fill

    # Print Combined Score
    pdfobj.set_font(style="B")
    pdfobj.set_fill_color(200, 200, 200)
    pdfobj.set_text_color(0)
    pdfobj.cell(80, 8, txt="Combined Score (Descriptive)", border=1, fill=True)
    pdfobj.cell(60, 8, txt=str(combined_score), align='C', border=1, fill=True)
    pdfobj.cell(0, 8, txt="", border=1, fill=True)
    pdfobj.ln()

    pdfobj.set_font(style="")
    pdfobj.set_text_color(0)
    pdfobj.set_margins(0, 0, 0)

def plot_tscores(pdfobj, col1: list, col2: list, 
                topproblemareas: list):
    M = 8
    LIGHTBLUE = (224, 235, 255)
    pdfobj.ln(40)
    pdfobj.set_left_margin(M)
    pdfobj.set_right_margin(M)
    pdfobj.set_fill_color(*LIGHTBLUE)
    # pdfobj.set_text_color(0)

    pdfobj.cell(100,9, txt=col1[0], align='C', border=1)
    pdfobj.cell(0,9, txt=str(col2[0]), align='C', border=1)
    pdfobj.ln()

    fill = True
    for category, score in zip(col1[1:], col2[1:]):
        if (category in topproblemareas):
            fill = True
            pdfobj.set_font(style="B")
            # pdfobj.set_fill_color(187, 104, 101)
            # pdfobj.set_fill_color(222, 140, 51)
            # pdfobj.set_fill_color(171, 107, 39)
            # pdfobj.set_fill_color(220, 218, 131)
            # pdfobj.set_fill_color(169, 167, 100)
            pdfobj.set_fill_color(171, 107, 39)
            # pdfobj.set_fill_color(118, 136, 220)
            # pdfobj.set_fill_color(220, 136, 118)

            pdfobj.set_text_color(255)
        else:
            # pdfobj.set_fill_color(224, 235, 255)
            pdfobj.set_font(style="")
            pdfobj.set_fill_color(*LIGHTBLUE)
            pdfobj.set_text_color(0)

        pdfobj.cell(100,8, txt=category, border=1, fill=fill)
        pdfobj.cell(0,8, txt=str(score), align='C', border=1, fill=fill)
        pdfobj.ln()
        fill = not fill
    pdfobj.set_font(style="")
    pdfobj.set_text_color(0)
    pdfobj.set_margins(0, 0, 0)

# Unused and Deprecated function
def plot_problem_areas(pdfobj, col: list, 
                        xpos: int, ypos: int = None):
    width = 60
    pdfobj.set_font_size(20)
    # pdfobj.set_left_margin(7)
    pdfobj.set_line_width(.7)
    pdfobj.set_fill_color(149, 83, 81)
    pdfobj.set_text_color(255)
    pdfobj.ln(ypos)
    pdfobj.set_x(xpos)
    pdfobj.set_font(style='UB')
    pdfobj.cell(width, 10, "Problem Areas", align='C', border='TB', fill=1)
    pdfobj.ln()
    pdfobj.set_x(xpos)
    pdfobj.set_fill_color(201, 112, 109)
    pdfobj.cell(width, 7, fill=1)

    pdfobj.set_font(style='B')
    pdfobj.set_font_size(12)
    for var in col:
        pdfobj.ln()
        pdfobj.set_x(xpos)
        # pdfobj.cell(50, 7, txt=var, align='C', border='TB', fill=1)
        pdfobj.cell(width, 7, txt=var, align='C', fill=1)
    pdfobj.ln()
    pdfobj.set_x(xpos)
    pdfobj.cell(width, 7, border='B', fill=1)
    
    # Revert all styling
    pdfobj.set_font_size(__DEF_FSIZE)
    pdfobj.set_text_color(0)
    pdfobj.set_font(style="")
    # pdfobj.set_fill_color(255)


def Create_All_Reports(dirpath: str, tscoreslist: list, data: list, allquestions: list,
                        graphs: dict, survey_id: int, codenames: list = None,
                        whichdepartment: str = None, version: str = 'v1', scoring_results: list = None) -> str:

    con1 = sqlite3.connect(config.DB)
    cur = con1.cursor()
    # cur.execute("""SELECT student_name, student_codename FROM tblSurveyReports 
        # WHERE survey_id=?""", (survey_id, ))
    # name_codename_map = {}
    # rows = cur.fetchall()
    # print(cur.fetchall())
    # print(rows)
    # for na, cona in rows:
    #     print(na, cona)
    #     name_codename_map[na] = cona 
        # print(na, cona )
    cur.execute("""DELETE FROM tblSurveyReports WHERE survey_id = ?""",
        (str(survey_id), ))

    created_codenames = set()
    for gi, stu in enumerate(graphs, start=1):
        count = 1
        codename = ''
        if (codenames is None):
            codename = generate_codename(data[gi])
            while (f'{codename}{count:03}' in created_codenames):
                count += 1
            codename = f'{codename}{count:03}'
            created_codenames.add(codename)
        else:
            codename = codenames[gi-1]

        if debug_setting:
            outfile_name = f"{gi}-{codename}.pdf"
        else:
            outfile_name = f"{codename}.pdf"
        outfile_name = os.path.join(dirpath, outfile_name)

        if version == 'v2':
            if scoring_results is None:
                raise ValueError("scoring_results must be provided for v2")
            
            sr = scoring_results[gi - 1]
            critical_flag = sr["critical_safety"]["triggered"]
            
            scores = []
            bands = []
            domain_codes = ['AN', 'DP', 'SI', 'SA', 'SE', 'IP', 'FP', 'AS', 'CC']
            problemareas = []
            
            for d_code, d_name in zip(domain_codes, ['Anxiety', 'Depression', 'Suicidal Ideation', 'Substance Abuse', 'Self-Esteem Problems', 'Interpersonal Problems', 'Family Problems', 'Academic Stress', 'Career Concerns']):
                s = sr["domain_scores"][d_name]
                b = sr["domain_bands"][d_name]
                scores.append(s)
                bands.append(b)
                if b in ('Moderate Relative', 'Higher Relative'):
                    problemareas.append(d_name)

            tscores = ['Score'] + scores
            combined_score = sum(scores)
            maxtscore = max(scores) # Just for safety note fallback
            
            student_name = data[gi][0] if len(data[gi]) > 0 else 'Unknown'
            if len(data[gi]) == 5:
                institute = data[gi][2]
                course = data[gi][3]
                year = data[gi][4]
            else:
                institute = data[gi][7] if len(data[gi]) > 7 else 'Unknown'
                course = data[gi][8] if len(data[gi]) > 8 else 'Unknown'
                year = data[gi][9] if len(data[gi]) > 9 else 'Unknown'
                
            import reportutility_v2 as rutil_v2
            rutil_v2.create_v2_report(os.path.join(dirpath,outfile_name), student_name, course, year, institute, scores, bands, critical_flag)
            
            con1.commit()
        # SURVEY_ID, STU_NAME, EMAIL, GUARDIAN, AGE, GENDER, MOBILE, INSTITUTE, STREAM, YEAR, MONTHLY_FAMILY_INCOME, FILE, CODENAME
        if version == 'v2':
            if len(data[gi]) == 5:
                # Name, Age, Institute, Course, Year
                db_data = (data[gi][0], '', '', data[gi][1], '', '', data[gi][2], data[gi][3], data[gi][4], '')
            else:
                # Pad or truncate to 10 elements
                db_data = tuple(data[gi][:10]) + ('',) * max(0, 10 - len(data[gi]))
        else:
            db_data = tuple(data[gi][:10]) + ('',) * max(0, 10 - len(data[gi]))
            
        cur.execute("""INSERT INTO tblSurveyReports(survey_id, student_codename, 
            student_name, email, guardian_name, age, gender, mobile_number, 
            institute, stream, year, monthly_family_income, tot_problem_areas,
            problem_areas, report_file, version) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (survey_id, codename, *db_data, len(problemareas),', '.join(problemareas), outfile_name, version))
        con1.commit()
    con1.close()
    clean_up(__GRAPHS_DIR)

    return dirpath
