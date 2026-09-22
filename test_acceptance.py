import tscoreutility as tsc


scale = {0: 'Never', 1: 'Rarely', 2: 'Sometimes', 3: 'Often', 4: 'Almost Always'}


headers = ['Student Name', 'Roll Number', 'Course', 'Year', 'Institute'] + [f'Q{i}' for i in range(1, 55)]




t1_responses = ['Never'] * 54
t1 = ['Test 1 (All Never)', '1', 'BA', '1', 'Acropolis'] + t1_responses




t2_responses = ['Almost Always'] * 54
t2 = ['Test 2 (All Almost Always)', '2', 'BA', '1', 'Acropolis'] + t2_responses




t4_responses = ['Never'] * 54

t4_responses[38] = 'Rarely' 
t4 = ['Test 4 (Low Total + Crit)', '4', 'BA', '1', 'Acropolis'] + t4_responses






targets = {
    'Anxiety': 7, 'Depression': 7, 'Suicidal Ideation': 5, 
    'Substance Abuse': 4, 'Self-Esteem Problems': 4, 'Interpersonal Problems': 4, 
    'Family Problems': 11, 'Academic Stress': 7, 'Career Concerns': 17
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

t3_numeric = [0] * 54

for dom, target in targets.items():
    rem = target
    for q in domain_mapping[dom]:
        if rem > 0:
            val = min(rem, 4)
            t3_numeric[q-1] = val
            rem -= val


t3_numeric[21-1] = 0 
t3_numeric[30-1] = 0 
t3_numeric[39-1] = 4 
t3_numeric[3-1]  = 1 
t3_numeric[12-1] = 0 
t3_numeric[48-1] = 0 

t3_responses = [scale[x] for x in t3_numeric]
t3 = ['Test 3 (Dummy case)', '3', 'BA', '1', 'Acropolis'] + t3_responses





data = [headers, t1, t2, t3, t4]


T_Scores_Of_All_Students, Student_Imp_Data, AllQuestions, Raw_Scores, scoring_results = tsc.Tscores_And_Students_ImpData(data)


for i, res in enumerate(scoring_results):
    print(f"--- {res['student_data'][0]} ---")
    print(f"Combined Score: {T_Scores_Of_All_Students[i+1][-1]}")
    print(f"Domain Scores: {res['domain_scores']}")
    print(f"Critical Safety Triggered: {res['critical_safety']['triggered']}")
    print(f"Triggered Items: {res['critical_safety']['triggered_items']}\n")