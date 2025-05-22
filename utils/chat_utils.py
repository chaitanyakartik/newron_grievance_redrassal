import vertexai 
from vertexai.generative_models import GenerativeModel, ChatSession, Part, Content
import json
import os
from dotenv import load_dotenv
from typing import List, Optional, Union
from utils.constants import department_tree, QUERY_CLASSIFIER_PROMPT, GENERATE_RELEVANT_QUESTIONS_PROMPT, TRANSLATE_QUERY_PROMPT
load_dotenv()

from utils.models import Gemini_Model_VertexAI_With_History, g1f

generate_content = g1f.generate_content

file_path = "utils/Agriculture_tree.json"
with open(file_path, "r") as file:
    agriculture_tree = json.load(file)

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")

vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)

class History:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

async def convert_history_to_gemini_format(history: Optional[List[History]]):
    gemini_history = []
    if history:
        for item in history:
            gemini_history.append(Content(role=item.role, parts=[Part.from_text(item.content)]))
    return gemini_history

async def query_classifier(query: str, history: Optional[List[History]], dept_path:List[str],chat_session_id: str):

    ## Returns department path if found, or returns questions for more data

    if history!=[]:
        formatted_history=await convert_history_to_gemini_format(history) 
    else:
        formatted_history=[]

    status, ans, path = await attempt_classification(query=query, tree=agriculture_tree,path=[],level=0,history=formatted_history)

    if status == "success":
        return "The department path is: " + ans, path
    else:
        return ans, path

async def attempt_classification(query: str, tree: List,path: List[str],level: int,history: List):
    if level==4:
        return "success",path
    
    department_list = await get_current_level_options(tree=tree, level=level, parent=path[-1] if path else None)

    template_parts = (
        QUERY_CLASSIFIER_PROMPT,
        f"User Query: {query}",
        f"Current Level Department Options (topic and summary): {json.dumps(department_list, indent=2)}",
        f"Write a clarifying question in JSON format only."
    )

    template = "\n".join(template_parts)
    
    model = Gemini_Model_VertexAI_With_History(model_name="gemini-2.5-flash-preview-05-20", chat_history=history)
    response = model.generate(template)
    print (response)

    result = response
    if result["status"]=="found":
        new_path=path + [result.get("department")]
        return await attempt_classification(query=query, tree=tree, path=new_path, level=level+1,history=history)
    else:
        question=await generate_relevant_questions(query=query, current_level_options=department_list,history=history)
        return "failure", question, path

async def get_current_level_options(tree: list, level: int, parent: str):
    def find_nodes_at_level(nodes, current_level, target_level, parent_topic):
        results = []
        for node in nodes:
            if target_level == 0:
                results.append(node)
            elif current_level == target_level - 1 and node.get("topic") == parent_topic:
                return node.get("sub_departments", [])
            else:
                sub_depts = node.get("sub_departments", [])
                deeper = find_nodes_at_level(sub_depts, current_level + 1, target_level, parent_topic)
                if deeper:
                    return deeper
        return results if target_level == 0 else []

    return find_nodes_at_level(tree, 0, level, parent)

async def generate_relevant_questions(query: str, current_level_options: list, history: list):
    template_parts=[
        GENERATE_RELEVANT_QUESTIONS_PROMPT,
        f"User Query: {query}",
        f"Current Level Department Options (topic and summary): {json.dumps(current_level_options, indent=2)}",
        f"Chat History: {history}",
        f"Write a clarifying question in JSON format only."
    ]

    template = "\n\n".join(template_parts)
    response=generate_content(
        [Content(role="user", parts=[Part.from_text(template)])],
        generation_config={
            "temperature": 0.125,
            "response_mime_type": "application/json",
        },
    )
    result = json.loads(response.text).get("clarifying_question", "")
    return result


def translate_query(query: str, target_language="English"):
    template_parts=[
        TRANSLATE_QUERY_PROMPT,
        f"Translate the following query to {target_language}:",
        f"User Query: {query}"
    ]

    template = "\n\n".join(template_parts)
    response=generate_content(
        [Content(role="user", parts=[Part.from_text(template)])],
        generation_config={
            "temperature": 0.125,
            "response_mime_type": "application/json",
        },
    )
    result = json.loads(response.text).get("translated_query", "")
    print(result)
    return result

    