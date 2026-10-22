from tqdm import tqdm
import config
import csv
import os
import openpyxl as op
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dirutility import create_dir

def Parse_Csv_To_List(path):
    
    with open(path) as file_object:
        reader_file = csv.reader(file_object)
        Raw_Data = list(reader_file)
    return Raw_Data


def Parse_Excel_To_List(path):
    """ 
        Parse a given excel sheet and return list. 
        The data to be parsed should be either in first sheet of excel file or 
        sheet should be named 'Raw Data' (case insensitive).
    """
    WorkBook = op.load_workbook(path)       #WorkBook in which data is available
    DEFAULT_SHEET = "Raw Data"
    try:
        Sheet = WorkBook[DEFAULT_SHEET]          #Particular Sheet in Workbook
    except KeyError as kerr:
        # There is a possiblity that excel file contains 'Raw data' sheet but
        # the letters could be in uppercase or lowercase and cause a mismatch
        DEFAULT_SHEET = DEFAULT_SHEET.lower()
        for sheet in WorkBook.sheetnames:
            if DEFAULT_SHEET == sheet.lower():
                Sheet = sheet
                break
        else:
        # if for-loop doesn't break then it means there was no Raw data sheet in
        # excel file and thus as backup we select the first sheet
            FIRST_SHEET = WorkBook.sheetnames[0]
            Sheet = WorkBook[FIRST_SHEET]
            # Sheet = WorkBook.active               #Last sheet found in excel        
    except Exception as e:
        # Unknown/Unexpected error occurred.
        print(f"Exception, at line {e.__traceback__.tb_lineno},",  *e.args)
        print(e.__traceback__.tb_frame, "\n")
        return []

    Total_rows = Sheet.max_row              #Total no. of rows in Sheet
    Total_clms = Sheet.max_column           #Total no. of coloms in Sheet

    RawData = []

    for i in range(1,Total_rows+1):         #Sheet data --->Data(It is 2d list)
        temp = []
        for j in range(1,Total_clms+1):
            temp.append(str(Sheet.cell(i,j).value))
        RawData.append(temp)

    WorkBook.close()
    return RawData


def Scores(value,clmNo):
    if clmNo==20 or clmNo==29 or clmNo==33 or clmNo==38 or clmNo==47 or clmNo==52 or clmNo==58 or clmNo==65 or clmNo==84 or clmNo==101:
       d={
        #'FALSE':4,
        'false':4,
        'slightly true':3,
        'mainly true':2,
        'very true':1
         } 
    else:
        d={
        #'FALSE':1,
        'false':1,
        'slightly true':2,
        'mainly true':3,
        'very true':4
         }     
    return d.get(value.strip().lower(), value)


def T_Scores(Name,value):
    d = {"AN": {12: 30, 13: 34, 14: 38, 15: 40, 16: 43, 17: 44, 18: 46, 19: 48, 20: 49, 21: 51, 22: 52, 23: 53, 24: 54, 25: 56, 26: 57, 27: 58, 28: 59, 29: 60, 30: 61, 31: 62, 32: 63, 33: 64, 34: 65, 35: 66, 36: 67, 37: 68, 38: 69, 39: 70, 40: 71, 41: 72, 42: 73, 43: 74, 44: 75, 45: 77, 46: 78, 47: 78, 48: 80},
         "DP": {12: 27, 13: 38, 14: 43, 15: 46, 16: 49, 17: 51, 18: 53, 19: 54, 20: 55, 21: 57, 22: 58, 23: 59, 24: 60, 25: 61, 26: 62, 27: 63, 28: 64, 29: 65, 30: 66, 31: 67, 32: 68, 33: 69, 34: 70, 35: 71, 36: 72, 37: 73, 38: 74, 39: 75, 40: 77, 41: 78, 42: 78, 43: 78, 44: 79, 45: 79, 46: 79, 47: 80, 48: 80},
         "SI": {12: 44, 13: 50, 14: 54, 15: 56, 16: 59, 17: 60, 18: 62, 19: 63, 20: 64, 21: 65, 22: 66, 23: 67, 24: 68, 25: 69, 26: 69, 27: 70, 28: 71, 29: 71, 30: 72, 31: 73, 32: 73, 33: 73, 34: 74, 35: 74, 36: 74, 37: 75, 38: 75, 39: 75, 40: 76, 41: 76, 42: 76, 43: 77, 44: 77, 45: 78, 46: 78, 47: 79, 48: 80},
         "SA": {12: 39, 13: 45, 14: 48, 15: 51, 16: 53, 17: 54, 18: 56, 19: 57, 20: 58, 21: 59, 22: 60, 23: 61, 24: 62, 25: 63, 26: 64, 27: 65, 28: 65, 29: 66, 30: 67, 31: 68, 32: 69, 33: 70, 34: 70, 35: 71, 36: 72, 37: 73, 38: 74, 39: 75, 40: 75, 41: 76, 42: 76, 43: 77, 44: 77, 45: 78, 46: 78, 47: 79, 48: 80},
         "SE": {12: 23, 13: 30, 14: 34, 15: 38, 16: 40, 17: 43, 18: 45, 19: 47, 20: 48, 21: 50, 22: 51, 23: 53, 24: 54, 25: 55, 26: 57, 27: 58, 28: 59, 29: 60, 30: 61, 31: 62, 32: 63, 33: 64, 34: 65, 35: 66, 36: 67, 37: 68, 38: 69, 39: 70, 40: 71, 41: 72, 42: 73, 43: 74, 44: 75, 45: 76, 46: 77, 47: 78, 48: 80},
         "IP": {12: 29, 13: 34, 14: 37, 15: 40, 16: 43, 17: 45, 18: 47, 19: 48, 20: 50, 21: 52, 22: 53, 23: 54, 24: 56, 25: 57, 26: 58, 27: 59, 28: 60, 29: 62, 30: 63, 31: 64, 32: 65, 33: 66, 34: 67, 35: 68, 36: 70, 37: 71, 38: 72, 39: 73, 40: 74, 41: 75, 42: 77, 43: 78, 44: 80, 45: 80, 46: 80, 47: 80, 48: 80},
         "FP": {12: 32, 13: 38, 14: 42, 15: 45, 16: 47, 17: 49, 18: 51, 19: 52, 20: 54, 21: 55, 22: 56, 23: 57, 24: 58, 25: 59, 26: 60, 27: 61, 28: 62, 29: 63, 30: 64, 31: 65, 32: 66, 33: 66, 34: 67, 35: 68, 36: 69, 37: 70, 38: 71, 39: 71, 40: 72, 41: 73, 42: 74, 43: 75, 44: 76, 45: 77, 46: 78, 47: 79, 48: 80},
         "AP": {12: 28, 13: 31, 14: 34, 15: 36, 16: 38, 17: 40, 18: 42, 19: 44, 20: 45, 21: 47, 22: 48, 23: 50, 24: 51, 25: 52, 26: 54, 27: 55, 28: 56, 29: 57, 30: 58, 31: 60, 32: 61, 33: 62, 34: 63, 35: 64, 36: 65, 37: 66, 38: 67, 39: 69, 40: 70, 41: 71, 42: 72, 43: 73, 44: 74, 45: 75, 46: 76, 47: 77, 48: 78},
         "CP": {12: 36, 13: 41, 14: 44, 15: 46, 16: 48, 17: 50, 18: 51, 19: 52, 20: 53, 21: 54, 22: 55, 23: 56, 24: 57, 25: 58, 26: 59, 27: 59, 28: 60, 29: 61, 30: 62, 31: 62, 32: 63, 33: 64, 34: 65, 35: 65, 36: 66, 37: 67, 38: 68, 39: 69, 40: 69, 41: 70, 42: 71, 43: 72, 44: 74, 45: 75, 46: 76, 47: 78, 48: 80}
         }
    return d[Name][value]


def Detect_Version_And_Offsets(data):
    if not data or len(data) == 0:
        raise ValueError("Empty data")
    headers = data[0]
    
    # Strip empty trailing columns and literal 'None' strings produced by openpyxl
    non_empty_headers = [h for h in headers if h is not None and str(h).strip() not in ('', 'None')]
    
    question_start_idx = -1
    for i, h in enumerate(non_empty_headers):
        text = str(h).upper()
        # V2 starts with 'QUESTION [1.', V1 might vary
        if 'QUESTION' in text or '[1.' in text or 'NERVOUS' in text:
            question_start_idx = i
            break
            
    if question_start_idx == -1:
        # Fallback based on known counts
        if len(non_empty_headers) >= 54 and len(non_empty_headers) < 100:
            question_start_idx = len(non_empty_headers) - 54
        elif len(non_empty_headers) >= 108:
            question_start_idx = len(non_empty_headers) - 108
        else:
            raise ValueError(f"Could not detect question start index. Total non-empty columns: {len(non_empty_headers)}")
            
    # Count exactly how many columns look like questions
    actual_question_count = sum(1 for h in headers if 'question' in str(h).strip().lower())
    
    if actual_question_count == 54:
        version = 'v2'
    elif actual_question_count == 108:
        version = 'v1'
    else:
        # Fallback to positional calculation if "QUESTION" string wasn't reliable
        positional_count = len(non_empty_headers) - question_start_idx
        if positional_count == 54:
            version = 'v2'
        elif positional_count == 108:
            version = 'v1'
        else:
            raise ValueError(
                f"Unsupported questionnaire structure: "
                f"{positional_count} question columns detected"
            )
        
    return version, question_start_idx, len(non_empty_headers)

def normalize_response(value):
    if value is None:
        raise ValueError("Response is empty")

    text = str(value).strip().lower()

    if "almost always" in text:
        return 4
    if "often" in text:
        return 3
    if "sometimes" in text:
        return 2
    if "rarely" in text:
        return 1
    if "never" in text:
        return 0

    raise ValueError(f"Unsupported response value: {value!r}")

def Scores_v2(value):
    return normalize_response(value)

def get_band_v2(domain_code, score):
    bands = {
        'SA': [(4, 'Lower'), (9, 'Mild'), (15, 'Moderate'), (24, 'Higher')],
        'AN': [(5, 'Lower'), (9, 'Mild'), (14, 'Moderate'), (24, 'Higher')],
        'DP': [(4, 'Lower'), (8, 'Mild'), (14, 'Moderate'), (24, 'Higher')],
        'SI': [(0, 'Lower'), (2, 'Mild'), (5, 'Moderate'), (24, 'Higher')],
        'SE': [(2, 'Lower'), (6, 'Mild'), (11, 'Moderate'), (24, 'Higher')],
        'IP': [(4, 'Lower'), (8, 'Mild'), (13, 'Moderate'), (24, 'Higher')],
        'FP': [(2, 'Lower'), (6, 'Mild'), (10, 'Moderate'), (24, 'Higher')],
        'AS': [(4, 'Lower'), (8, 'Mild'), (13, 'Moderate'), (24, 'Higher')],
        'CC': [(4, 'Lower'), (9, 'Mild'), (15, 'Moderate'), (24, 'Higher')]
    }
    for upper_bound, label in bands[domain_code]:
        if score <= upper_bound:
            return label
    return 'Higher'

def Tscores_And_Students_ImpData(RawData, version=None, question_start_idx=None, total_non_empty_cols=None, col_map=None):
    if version is None:
        version, question_start_idx, total_non_empty_cols = Detect_Version_And_Offsets(RawData)
    Total_rows = len(RawData)
    Total_cols = total_non_empty_cols

    Student_Imp_Data = []
    AllQuestions = []
    scoring_results = []
    
    if version == 'v2':
        Raw_Scores = [['AN','DP','SI','SA','SE','IP','FP','AS','CC']]
        T_Scores_Of_All_Students = [['AN-Band','DP-Band','SI-Band','SA-Band','SE-Band','IP-Band','FP-Band','AS-Band','CC-Band', 'COMBINED']]
    else:
        Raw_Scores = [['AN','DP','SI','SA','SE','IP','FP','AP','CP']]
        T_Scores_Of_All_Students = [['T-AN','T-DP','T-SI','T-SA','T-SE','T-IP','T-FP','T-AP','T-CP']]

    for i in range(0,Total_rows):
        student = []
        OneRowQuestions = []
        for j in range(0,Total_cols):
            if j < question_start_idx:
                if version == 'v1' and j < 3:
                    continue
                student.append(RawData[i][j])
            else:
                OneRowQuestions.append(RawData[i][j])
                
        if version == 'v2' and col_map:
            OneRowQuestions = [RawData[i][col_map['questions'][q_num]] for q_num in range(1, 55)]
            meta = col_map['metadata']
            if i == 0:
                student = ["Name", "Age", "Institute", "Course", "Year", "Email", "Mobile", "Gender", "Guardian", "Income"]
            else:
                name_idx = meta.get('name', -1)
                age_idx = meta.get('age', -1)
                inst_idx = meta.get('institute', -1)
                course_idx = meta.get('course', -1)
                year_idx = meta.get('year', -1)
                
                email_idx = meta.get('email', -1)
                mobile_idx = meta.get('mobile', -1)
                gender_idx = meta.get('gender', -1)
                guardian_idx = meta.get('guardian', -1)
                income_idx = meta.get('income', -1)
                
                student = [
                    RawData[i][name_idx] if name_idx != -1 else '',
                    RawData[i][age_idx] if age_idx != -1 else '',
                    RawData[i][inst_idx] if inst_idx != -1 else '',
                    RawData[i][course_idx] if course_idx != -1 else '',
                    RawData[i][year_idx] if year_idx != -1 else '',
                    RawData[i][email_idx] if email_idx != -1 else '',
                    RawData[i][mobile_idx] if mobile_idx != -1 else '',
                    RawData[i][gender_idx] if gender_idx != -1 else '',
                    RawData[i][guardian_idx] if guardian_idx != -1 else '',
                    RawData[i][income_idx] if income_idx != -1 else ''
                ]

        Student_Imp_Data.append(student)
        AllQuestions.append(OneRowQuestions)

    for i in range(1,Total_rows):
        temp = []
        temp_Raw_Scores = []
        j = question_start_idx
        AN = DP = SI = SA = SE = IP = FP = AP_AS = CP_CC = 0
        
        if version == 'v2':
            # V2 has 54 questions, 6 per domain
            if col_map:
                raw_responses = [RawData[i][col_map['questions'][q_num]] for q_num in range(1, 55)]
            else:
                raw_responses = [RawData[i][col] for col in range(question_start_idx, Total_cols)]
            # Assertions
            is_valid = True
            errors = []
            numeric_responses = []
            missing_questions = []

            for q_idx, val in enumerate(raw_responses, start=1):
                val_str = str(val).strip().lower()
                if val is None or val_str in ['', 'none', 'nan']:
                    missing_questions.append(f"Q{q_idx}")
                    numeric_responses.append(0)
                    continue
                try:
                    numeric_responses.append(Scores_v2(val))
                except Exception as e:
                    missing_questions.append(f"Q{q_idx}")
                    numeric_responses.append(0)

            if missing_questions:
                is_valid = False
                errors.append("Unanswered questions detected.")
                
            if len(numeric_responses) != 54:
                is_valid = False
                errors.append(f"Expected 54 responses, got {len(numeric_responses)}")
            if not all(score in {0, 1, 2, 3, 4} for score in numeric_responses):
                is_valid = False
                errors.append("Scores must be in 0-4")
            
            domain_names = ['Anxiety', 'Depression', 'Suicidal Ideation', 'Substance Abuse', 'Self-Esteem Problems', 'Interpersonal Problems', 'Family Problems', 'Academic Stress', 'Career Concerns']
            domain_codes = {
                'Anxiety': 'AN', 'Depression': 'DP', 'Suicidal Ideation': 'SI', 
                'Substance Abuse': 'SA', 'Self-Esteem Problems': 'SE', 
                'Interpersonal Problems': 'IP', 'Family Problems': 'FP', 
                'Academic Stress': 'AS', 'Career Concerns': 'CC'
            }
            domain_mapping = {
                'Anxiety': [1, 10, 19, 28, 37, 46],
                'Depression': [2, 11, 20, 29, 38, 47],
                'Suicidal Ideation': [3, 12, 21, 30, 39, 48],
                'Substance Abuse': [4, 13, 22, 31, 40, 49],
                'Self-Esteem Problems': [5, 14, 23, 32, 41, 50],
                'Interpersonal Problems': [6, 15, 24, 33, 42, 51],
                'Family Problems': [7, 16, 25, 34, 43, 52],
                'Academic Stress': [8, 17, 26, 35, 44, 53],
                'Career Concerns': [9, 18, 27, 36, 45, 54],
            }
            
            
            import hashlib
            # Dynamically resolve student name based on headers
            student_data = [RawData[i][col] for col in range(question_start_idx)]
            header_data = [str(RawData[0][col]).lower().strip() for col in range(question_start_idx)]
            
            if col_map:
                name_idx = col_map['metadata'].get('name', -1)
            else:
                name_idx = header_indices.get('name', -1)
            
            if name_idx == -1:
                is_valid = False
                errors.append("Could not identify student name column in headers.")
                student_name = "Unknown"
            else:
                student_name = student_data[name_idx] if len(student_data) > name_idx else "Unknown"
            
            # Deterministic Record ID
            row_str = '|'.join([str(x).strip().lower() for x in student_data])
            record_id = hashlib.md5(row_str.encode('utf-8')).hexdigest()[:12]
            
            domain_scores = {}
            domain_bands = {}
            safety_triggered = False
            critical_items = [21, 30, 39]
            safety_responses = {}
            triggered_items = []
            combined_score = 0
            
            if is_valid:
                for d in domain_names:
                    score = sum(numeric_responses[q - 1] for q in domain_mapping[d])
                    domain_scores[d] = score
                    band = get_band_v2(domain_codes[d], score)
                    domain_bands[d] = f"{band} Relative"
                
                combined_score = sum(numeric_responses)
                
                # Critical Safety Logic
                for q in critical_items:
                    val = numeric_responses[q - 1]
                    safety_responses[q] = val
                    if val > 0:
                        safety_triggered = True
                        triggered_items.append(q)
            
            # Build Audit Trace
            audit_trace = [
                f"Student: {student_name}",
                "Detected version: v2",
                f"Total response count: {len(numeric_responses)}",
                f"Combined score: {combined_score if is_valid else 'N/A'}",
                ""
            ]
            if is_valid:
                for d in domain_names:
                    q_nums = domain_mapping[d]
                    q_vals = [numeric_responses[q - 1] for q in q_nums]
                    audit_trace.append(f"Domain: {d}")
                    audit_trace.append(f"Question numbers: {', '.join(map(str, q_nums))}")
                    audit_trace.append(f"Question numeric values: {', '.join(map(str, q_vals))}")
                    audit_trace.append(f"Calculation: {'+'.join(map(str, q_vals))}")
                    audit_trace.append(f"Domain score: {domain_scores[d]}/24")
                    audit_trace.append("Maximum: 24")
                    audit_trace.append(f"Relative band or Substance Abuse status: {domain_bands[d]}")
                    audit_trace.append("")
            
            scoring_result = {
                "student_id": record_id,
                "student_name": student_name,
                "student_data": student_data,
                "header_data": header_data,
                "questionnaire_version": "V2",
                "numeric_responses": numeric_responses,
                "domain_scores": domain_scores,
                "domain_bands": domain_bands,
                "critical_safety": {
                    "triggered": safety_triggered,
                    "critical_question_numbers": critical_items,
                    "triggered_items": triggered_items,
                    "responses": safety_responses
                },
                "validation": {
                    "is_valid": is_valid,
                    "errors": errors,
                    "warnings": [],
                    "missing_questions": missing_questions
                },
                "audit_trace": audit_trace
            }
            scoring_results.append(scoring_result)
            
            # Legacy structures for compatibility
            temp_Raw_Scores = [domain_scores.get(d, 0) for d in domain_names]
            Raw_Scores.append(temp_Raw_Scores)
            T_Scores_Of_All_Students.append(temp_Raw_Scores + [combined_score if is_valid else 0])
        else:
            # V1 has 108 questions, 12 per domain
            count = 1
            j = question_start_idx
            numeric_vals = [Scores(RawData[i][col], col) for col in range(question_start_idx, Total_cols)]
            
            j = 0
            while count <= 12:
                AP_AS += numeric_vals[j]
                AN += numeric_vals[j+1]
                IP += numeric_vals[j+2]
                DP += numeric_vals[j+3]
                CP_CC += numeric_vals[j+4]
                SI += numeric_vals[j+5]
                SA += numeric_vals[j+6]
                SE += numeric_vals[j+7]
                FP += numeric_vals[j+8]
                j += 9
                count += 1
                
            temp.append(T_Scores("AN", AN))
            temp.append(T_Scores("DP", DP))
            temp.append(T_Scores("SI", SI))
            temp.append(T_Scores("SA", SA))
            temp.append(T_Scores("SE", SE))
            temp.append(T_Scores("IP", IP))
            temp.append(T_Scores("FP", FP))
            temp.append(T_Scores("AP", AP_AS))
            temp.append(T_Scores("CP", CP_CC))
            T_Scores_Of_All_Students.append(temp)

            temp_Raw_Scores.append(AN)
            temp_Raw_Scores.append(DP)
            temp_Raw_Scores.append(SI)
            temp_Raw_Scores.append(SA)
            temp_Raw_Scores.append(SE)
            temp_Raw_Scores.append(IP)
            temp_Raw_Scores.append(FP)
            temp_Raw_Scores.append(AP_AS)
            temp_Raw_Scores.append(CP_CC)
            Raw_Scores.append(temp_Raw_Scores)

    return T_Scores_Of_All_Students, Student_Imp_Data, AllQuestions, Raw_Scores, scoring_results


def Graph_Of_Tscores(Y_Axis_tscore, Student_Data, i, directory_path, version='v1'):
    
    if version == 'v2':
        X_Axis_Names = ['Anxiety','Depression','Suicidal Ideation','Substance Abuse','Self-esteem Problems','Interpersonal Problems','Family Problems','Academic Stress','Career Concerns']
        y_lim = 24
    else:
        X_Axis_Names = ['Anxiety','Depression','Suicidal Ideation','Substance Abuse','Self-esteem Problems','Interpersonal Problems','Family Problems','Academic Problems','Career Problems']
        y_lim = 80

    plt.rcParams['figure.figsize']=(8,5)
    plt.figure(facecolor="white")

    # Y_Axis_tscore includes the combined score at the end in V2, so we slice it to 9.
    Y_Axis_tscore = Y_Axis_tscore[:9]

    plt.plot(X_Axis_Names, Y_Axis_tscore, color="#1f77b4", marker='o') # Blue line
    plt.ylim(0, y_lim+3)
    
    plt.title("Assessment Summary - Domain Scores", fontweight="bold", fontsize=11)
    plt.ylabel(f"Score (out of {y_lim})", fontsize=9)
    plt.xlabel("Domain", fontsize=9)
    
    plt.xticks(rotation=40, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.gcf().subplots_adjust(bottom=0.25)
    
    plt.grid(axis='y', alpha=0.3)

    for k in range(len(X_Axis_Names)):
        plt.text(k, Y_Axis_tscore[k] + 0.5, str(Y_Axis_tscore[k]), ha='center', va="bottom", fontweight="bold", fontsize=8)

    Graph_Name = Student_Data[i][0] + str(i) + ".png"
    plt.savefig(os.path.join(directory_path, Graph_Name), bbox_inches="tight")
    plt.close()

    return Graph_Name


def Plot_Graphs(TScores, Student_Data, version='v1', ui_callback=None):
    """Returns a dictionary of Student-Name:Image-file pair"""
    Total_rows = len(TScores)      #Total no. of rows in Data
    Total_cols = len(TScores[0])   #Total no. of coloms in Data

    # Instead of list, a mapping of student-name to graph-image-path is more convenient and secure.
    # List_Of_Graphs = []
    folder = create_dir(config.TEMPDIR)
    Graphs = {}
    for i in range(1,Total_rows):
        if ui_callback:
            try:
                ui_callback(i, Total_rows - 1, f"Plotting Graph {i} of {Total_rows - 1}")
            except:
                pass
        Y_Axis_tscore = []
        for j in range(0,Total_cols):
            Y_Axis_tscore.append(TScores[i][j])
        # List_Of_Graphs.append(Graph_Of_Tscores(Y_Axis_tscore,Student_Data,i))  #For Making graph of row student
        
        Graphs[i] = Graph_Of_Tscores(Y_Axis_tscore,Student_Data,i,folder, version=version)
    
    # return List_Of_Graphs
    
    return Graphs
    # return {'abcd': 'sample-plot.png'}


if __name__ == '__main__':
    from pprint import pprint
    FILE = 'cas-copy.xlsx'
    FILE = '1-record-cas-sheet.xlsx'
    data = Parse_Excel_To_List(FILE)
    # pprint(data)
    tscdata, studata, allquestions, rawscores = Tscores_And_Students_ImpData(data)
    pprint(studata)
    pprint(tscdata)
    # pprint(rawscores)