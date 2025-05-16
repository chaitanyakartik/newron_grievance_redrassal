
department_tree = [
    {
        "topic": "Academics",
        "summary": "Issues related to courses, exams, grades, and faculty.",
        "sub_departments": [
            {
                "topic": "Courses",
                "summary": "Course content, scheduling, and course registration problems.",
                "sub_departments": [
                    {
                        "topic": "Electives",
                        "summary": "Selection or change of elective courses.",
                        "sub_departments": [
                            {
                                "topic": "Cross-department Electives",
                                "summary": "Issues with electives offered by other departments."
                            },
                            {
                                "topic": "Elective Capacity",
                                "summary": "Problems with full courses or unavailable elective seats."
                            }
                        ]
                    },
                    {
                        "topic": "Core Courses",
                        "summary": "Compulsory subject issues like prerequisites, material, or faculty."
                    }
                ]
            },
            {
                "topic": "Exams",
                "summary": "Exam schedules, re-evaluation, or unfair grading complaints."
            }
        ]
    },
    {
        "topic": "Hostel",
        "summary": "Problems related to accommodation, food, and hostel facilities.",
        "sub_departments": [
            {
                "topic": "Mess",
                "summary": "Food quality, billing, menu, and hygiene concerns.",
                "sub_departments": [
                    {
                        "topic": "Billing Issues",
                        "summary": "Incorrect charges or missing bill details."
                    },
                    {
                        "topic": "Food Quality",
                        "summary": "Complaints about taste, cleanliness, or food safety."
                    }
                ]
            },
            {
                "topic": "Room Allocation",
                "summary": "Allotment changes, roommate issues, or maintenance problems."
            }
        ]
    }
]

QUERY_CLASSIFIER_PROMPT = f"""
You are a classification assistant for a university grievance system.

Your task:
- Classify the user query into **one** of the department topics provided at the current level.
- If none of the options clearly match, return `"status": "not found"` and `"classified_department": null`.

Use the query, department options, and conversation history (if any) to make your decision.

Respond ONLY in the following JSON format:
{{
  "classified_department": "<Department Topic Name or null>",
  "status": "found" or "not found"
}}

---
"""
REFORMAT_QUERY_PROMPT = f"""
You are an assistant helping to rewrite a grievance query to make it complete and self-contained.

Task:
- Use the original query, the clarifying question asked, the user's answer, and the prior conversation (if any).
- Rewrite the query to include all relevant details from the chat so that it is clear, specific, and doesn't require further clarification.

Output only the improved, detailed version of the query in plain text. Do NOT include any explanations or extra formatting.

---

{{
  "rephrased_query": "<complete and specific query here>"
}}

"""

GENERATE_RELEVANT_QUESTIONS_PROMPT = f"""
You are an assistant in a grievance classification system.

Goal:
The user submitted a query, but it's not specific enough to classify into one of the available department options. Your task is to generate a **clear, concise clarifying question** that will help the user provide the exact information needed to choose one of the department topics listed below.

Instructions:
- The question should be natural and user-friendly.
- Use the original query, conversation history, and current department topics with their summaries.
- Focus only on the department level options provided — your question should help narrow down to one of them.

Respond ONLY in the following JSON format:
{{
  "clarifying_question": "<your follow-up question here>"
}}
---
Write a clarifying question in JSON format only.
"""

TRANSLATE_QUERY_PROMPT = f"""
You are an assistant in a grievance classification system.
Your task:
- Translate the user query into a different language.

Respond ONLY in the following JSON format:
{{
  "translated_query": "<translated query here>"
}}
"""