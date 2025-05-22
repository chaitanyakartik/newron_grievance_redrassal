import vertexai
import vertexai.generative_models
import json

class Gemini_Model_VertexAI_With_History():
    """
    This is done using chat sessions (gemini multiturn)
    Example chat history

    gemini_history = [
        {role: "user", parts: "What is the capital of France?"},
        {role: "model", parts: "The capital of France is Paris."},
    """
    def __init__(self,model_name="gemini-1.5-pro",chat_history=[]):
        vertexai.init()
        self.model = vertexai.generative_models.GenerativeModel(
            model_name=model_name,
            safety_settings={
                vertexai.generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: vertexai.generative_models.HarmBlockThreshold.BLOCK_NONE,
                vertexai.generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: vertexai.generative_models.HarmBlockThreshold.BLOCK_NONE,
                vertexai.generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: vertexai.generative_models.HarmBlockThreshold.BLOCK_NONE,
                vertexai.generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: vertexai.generative_models.HarmBlockThreshold.BLOCK_NONE,
            },
        )
        self.current_chat_session = vertexai.generative_models.ChatSession(model=self.model,history=chat_history)
        
    def generate(self,prompt: str):
        generation_config={
            "temperature": 0.5,
            "response_mime_type": "application/json",
        }

        response=self.current_chat_session.send_message(
            [prompt],
            generation_config=generation_config
        )

        response = json.loads(response.candidates[0].content.parts[0].text)
        return response


g1f = vertexai.generative_models.GenerativeModel(
    model_name="gemini-2.0-flash-001",
    safety_settings={
        vertexai.generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: vertexai.generative_models.HarmBlockThreshold.BLOCK_NONE,
        vertexai.generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: vertexai.generative_models.HarmBlockThreshold.BLOCK_NONE,
        vertexai.generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: vertexai.generative_models.HarmBlockThreshold.BLOCK_NONE,
        vertexai.generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: vertexai.generative_models.HarmBlockThreshold.BLOCK_NONE,
    },
)