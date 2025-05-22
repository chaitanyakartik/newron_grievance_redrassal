import vertexai 
from vertexai.generative_models import GenerativeModel, ChatSession, Part, Content
import json
import os
from dotenv import load_dotenv
from typing import List, Optional, Union
from utils.constants import department_tree, QUERY_CLASSIFIER_PROMPT, GENERATE_RELEVANT_QUESTIONS_PROMPT, TRANSLATE_QUERY_PROMPT
load_dotenv()

from datetime import datetime
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

async def get_history_from_sesh_id(chat_session_id: str):
    session_file_path = f"chat_history/{chat_session_id}.json"
    if not os.path.exists(session_file_path):
        raise FileNotFoundError(f"Chat session file not found for ID: {chat_session_id}")
    
    with open(session_file_path, "r") as file:
        session_data = json.load(file)
    
    history = []
    for entry in session_data.get("history", []):
        history.append(History(role=entry["role"], content=entry["content"]))
    
    return history, session_data.get("dept_path", [])


async def get_next_children(tree, dept_path):
    # Find the current node
    current_node = tree
    for dept in dept_path:
        found = False
        for node in current_node:
            if node.get("name") == dept:
                current_node = node.get("children", [])
                found = True
                break
        if not found:
            return []  # Path not found

    # Extract just the names from the children nodes
    return [child.get("name") for child in current_node]

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

async def update_dept_path(session_id: str, new_dept_path: List[str]):
    """
    Updates the department path in the session JSON file.
    
    Args:
        session_id: The unique session identifier
        new_dept_path: The updated department path list
    """
    # Create chat_history directory if it doesn't exist
    os.makedirs("chat_history", exist_ok=True)
    
    # Path to session file
    session_file_path = f"chat_history/{session_id}.json"
    
    # Load existing session data if it exists
    if os.path.exists(session_file_path):
        with open(session_file_path, "r") as file:
            session_data = json.load(file)
    else:
        # Create new session data if file doesn't exist
        session_data = {
            "session_id": session_id,
            "chat_history": [],
            "current_path": [],
            "last_updated": ""
        }
    
    # Update the department path and last_updated timestamp
    session_data["current_path"] = new_dept_path
    session_data["last_updated"] = datetime.now().isoformat()
    
    # Save the updated session data
    with open(session_file_path, "w") as file:
        json.dump(session_data, file, indent=2)


async def check_if_final_department(dept_path: List[str]) -> bool:
    """
    Checks if the current department path leads to a final (leaf) node with no children.
    
    Args:
        dept_path: The current department path list
    
    Returns:
        True if this is a final department (no children), False otherwise
    """
    if not dept_path:
        return False
    
    # Navigate to the current node
    current_node = agriculture_tree
    for dept in dept_path:
        found = False
        for node in current_node:
            if node.get("name") == dept:
                current_node = node.get("children", [])
                found = True
                break
        if not found:
            # Path not found in the tree
            return False
    
    # If current_node is empty or doesn't exist, we're at a leaf node
    if not current_node or len(current_node) == 0:
        return True
    
    # Check if the "children" key exists but is empty in the last node
    if dept_path:
        for node in agriculture_tree:
            current = node
            for dept in dept_path:
                found = False
                if isinstance(current, dict) and current.get("name") == dept:
                    found = True
                    if "children" not in current or not current["children"]:
                        return True
                    current = current["children"]
                    break
                elif isinstance(current, list):
                    for child in current:
                        if child.get("name") == dept:
                            found = True
                            current = child.get("children", [])
                            if not current:
                                return True
                            break
                if not found:
                    break
            if found:  # If we found the full path
                return False
    
    return False

async def query_classifier(query: str, chat_session_id: str):

    history, dept_path = await get_history_from_sesh_id(chat_session_id)
    formatted_history = await convert_history_to_gemini_format(history)
    next_children = await get_next_children(agriculture_tree, dept_path)

    nature, result = await attempt_classification(
        query=query,
        dept_path=dept_path,
        next_children=next_children,
        history=formatted_history,
        session_id=chat_session_id
    )

    if nature == "question":
        new_history, new_dept_path = await get_history_from_sesh_id(chat_session_id)
        return result, new_dept_path
    elif nature == "final_path":
        new_history, new_dept_path = await get_history_from_sesh_id(chat_session_id)
        return result, dept_path
    else:
        print("something broke")
        return None, dept_path

async def attempt_classification(
    query: str,
    dept_path: List[str],
    next_children: List[str],
    session_id: str ,
    history: Optional[List[Content]] = None
):
    template_parts = (
        QUERY_CLASSIFIER_PROMPT,
        f"User Query: {query}",
        f"Current Level Department Options (topic and summary): {json.dumps(next_children, indent=2)}",
        f"Write a clarifying question in JSON format only."
    )
    template = "\n".join(template_parts)
    model = Gemini_Model_VertexAI_With_History(model_name="gemini-2.5-flash-preview-05-20", chat_history=history)
    response = model.generate(template)
    print (response)

    result = response

    # Check if department is found
    if result.get("status") == "found":
        classified_dept = result.get("classified_department")
        new_dept_path= dept_path + [classified_dept]
        update_dept_path(session_id, new_dept_path)
        is_final = check_if_final_department(new_dept_path)

        if is_final==True:
            return "final_path", new_dept_path
        else:
            new_children = get_next_children(agriculture_tree, new_dept_path)
            return await attempt_classification(
                query=query,
                dept_path=new_dept_path,
                next_children=new_children,
                history=history,
                session_id=session_id
            )
        
    else: #result.get("status") == "not found"
        question = await generate_relevant_questions(query=query, current_level_options=next_children, history=history)
        return "question", question
    




