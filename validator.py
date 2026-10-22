import re
from typing import Dict, Tuple, Any

# English prefix fingerprints to validate that the question matches its number
EXPECTED_PREFIXES = {
    1: "i feel nervous or",
    2: "lately i have been",
    3: "i have felt that",
    4: "i drink alcohol smoke",
    5: "i frequently feel dissatisfied",
    6: "i find it hard",
    7: "there is often conflict",
    8: "i find it hard",
    9: "i am unsure which",
    10: "i find it hard",
    11: "i no longer enjoy",
    12: "i have thought about",
    13: "i have given up",
    14: "i compare myself to",
    15: "i often feel that",
    16: "it bothers me that",
    17: "i feel overwhelmed by",
    18: "i worry about finding",
    19: "my heart beats fast",
    20: "i feel tired even",
    21: "i have attempted suicide",
    22: "i have hidden or",
    23: "i find it hard",
    24: "i avoid social situations",
    25: "my family has very",
    26: "i find it hard",
    27: "i lack clarity in",
    28: "i feel restless and",
    29: "lately i find it",
    30: "i have thought of",
    31: "my drinking smoking or",
    32: "i doubt myself even",
    33: "i seem to disagree",
    34: "i find it hard",
    35: "i feel my grades",
    36: "i feel pressure from",
    37: "i have trouble sleeping",
    38: "i dont feel as",
    39: "i have thought about",
    40: "i have used alcohol",
    41: "i feel i do",
    42: "i find it hard",
    43: "i think about problems",
    44: "i delay my academic",
    45: "i do not have",
    46: "there are many times",
    47: "my eating or sleeping",
    48: "i can no longer",
    49: "when im stressed i",
    50: "i generally think badly",
    51: "i feel lonely even",
    52: "i feel distant from",
    53: "even after preparing well",
    54: "i feel anxious when",
}


def normalize_header(h):
    if not h: return ""
    import string
    return " ".join(str(h).lower().strip().split())

def validate_file_structure(headers: list) -> Tuple[bool, Dict[str, Any], list]:
    errors = []
    mapping = {
        'metadata': {},
        'questions': {}
    }
    
    GUARDIAN_KEYWORDS = ['guardian', 'parent', 'father', 'mother', 'माता', 'पिता', 'अभिभावक']
    found_metadata = {
        'name': [],
        'age': [],
        'institute': [],
        'course': [],
        'year': [],
        'email': [],
        'mobile': [],
        'gender': [],
        'guardian': [],
        'income': []
    }
    
    # 2. Question validation
    found_questions = {}
    
    for idx, h_raw in enumerate(headers):
        h = normalize_header(h_raw)
        if not h: continue
        
        # Regex to match QUESTION [XX...
        match = re.search(r'question\s*\[\s*(\d+)\.(.*?)\]', h)
        if not match:
            # Check for malformed missing dot: QUESTION [17]
            malformed_match = re.search(r'question\s*\[\s*(\d+)\s*\]', h)
            if malformed_match:
                q_num = int(malformed_match.group(1))
                if 1 <= q_num <= 54:
                    errors.append(f"Malformed question header: Q{q_num} is missing its text.")
        else:
            q_num = int(match.group(1))
            q_text = match.group(2)
            
            if 1 <= q_num <= 54:
                if q_num in found_questions:
                    found_questions[q_num].append(idx)
                else:
                    found_questions[q_num] = [idx]
                    
                # Validate text matches expectation
                import string
                english_part = ''.join(c for c in q_text if c in string.ascii_lowercase + ' ').strip()
                # collapse multiple spaces
                english_part = " ".join(english_part.split())
                
                expected_prefix = " ".join(EXPECTED_PREFIXES[q_num].split()[:4])
                
                if expected_prefix not in english_part:
                    errors.append(f"Invalid question header text for Q{q_num}. Expected text similar to: '{EXPECTED_PREFIXES[q_num]}'")
        
        # Metadata matching (skip if it looks like a question to avoid false positives)
        if 'question' not in h:
            is_guardian = any(g in h for g in GUARDIAN_KEYWORDS)
            
            if any(x in h for x in ['name', 'student name', 'full name', 'first name', 'last name', 'नाम']):
                if 'institute' not in h and not is_guardian:
                    found_metadata['name'].append(idx)
                    
            if any(x in h for x in ['age', 'old', 'आयु', 'उम्र']):
                found_metadata['age'].append(idx)
                    
            if any(x in h for x in ['name of institute', 'institute', 'college', 'school', 'university']):
                found_metadata['institute'].append(idx)
                
            if any(x in h for x in ['course', 'stream', 'program', 'degree', 'class', 'batch']):
                found_metadata['course'].append(idx)
                
            if any(x in h for x in ['year', 'semester', 'grade']):
                found_metadata['year'].append(idx)
                
            if any(x in h for x in ['email', 'e-mail', 'mail id']):
                found_metadata['email'].append(idx)
                
            if any(x in h for x in ['mobile', 'phone', 'contact', 'whatsapp']):
                found_metadata['mobile'].append(idx)
                
            if any(x in h for x in ['gender', 'sex', 'लिंग']):
                found_metadata['gender'].append(idx)
                
            if is_guardian:
                found_metadata['guardian'].append(idx)
                
            if any(x in h for x in ['income', 'salary', 'earning', 'आय']):
                found_metadata['income'].append(idx)
            
    # Metadata validation rules
    required_meta = ['name', 'institute', 'course', 'year']
    for req in required_meta:
        if len(found_metadata[req]) == 0:
            errors.append(f"Missing required metadata column: {req.capitalize()}")
        elif len(found_metadata[req]) > 1:
            # We strictly reject if ambiguous to prevent corrupt mapping
            errors.append(f"Duplicate or ambiguous metadata columns found for: {req.capitalize()}")
        else:
            mapping['metadata'][req] = found_metadata[req][0]
            
    optional_meta = ['age', 'email', 'mobile', 'gender', 'guardian', 'income']
    for opt in optional_meta:
        if len(found_metadata[opt]) == 1:
            mapping['metadata'][opt] = found_metadata[opt][0]
            
    # Validate exactly 1 to 54
    for q_num in range(1, 55):
        if q_num not in found_questions:
            errors.append(f"Missing required question column: Q{q_num}")
        elif len(found_questions[q_num]) > 1:
            errors.append(f"Duplicate question column detected: Q{q_num}")
        else:
            mapping['questions'][q_num] = found_questions[q_num][0]
            
    is_valid = len(errors) == 0
    return is_valid, mapping, errors
