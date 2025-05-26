# Chat Interface Usage Manual

This document provides instructions on how to use the Streamlit Chat Interface.

## 1. Overview

The Chat Interface allows you to communicate with an assistant to help resolve grievances by identifying the correct department. It maintains a history of your conversation and displays the current classification path for your query.

## 2. Main Interface

The main screen is composed of the following elements:

* **Title**: "💬 Chat Interface" is displayed at the top.
* **Current Department Path**:
    * Located below the title, this section shows the department(s) the assistant has currently identified for your grievance.
    * The path is displayed in a breadcrumb format, for example:
        `Department A → Sub-Department B → Office C`
    * If no path has been determined yet, it will display "No classification path available yet".
* **Conversation Area**:
    * This is where your chat with the assistant takes place. It's a scrollable container labeled "Conversation".
    * Your messages will appear aligned to one side, and the assistant's responses will appear on the other.
    * If the conversation history is empty, it will display "No messages yet. Type your message below to start the conversation!"
* **Message Input**:
    * At the bottom of the screen, a text input field labeled "Type your message:" is available for you to enter your queries or commands.
    * Press Enter to send your message.

## 3. Sidebar

The sidebar on the left provides additional controls and information:

* **Debug Mode**:
    * A checkbox labeled "Debug Mode". When enabled, it provides more detailed technical information about API calls and session status in the sidebar.
* **Force API Health Check**:
    * A button that manually triggers a check of the backend API's health. The status (operational or error) will be displayed in the sidebar.
* **API Status**:
    * Displays the current connection status to the backend API.
* **Clear Conversation**:
    * A button that clears the displayed chat history in the current session. The underlying department path for the session (if any) will be reloaded.
* **New Session**:
    * A button that starts an entirely new chat. This will clear the current chat history, the resolved department path, and initiate a fresh session with the backend.
* **Session ID (Debug Mode only)**:
    * If "Debug Mode" is enabled, the current unique session identifier will be displayed at the bottom of the sidebar.

## 4. Chatting with the Assistant

1.  **Start a Conversation**: Type your initial grievance or question into the message input field at the bottom and press Enter.
2.  **Follow-up**: The assistant will respond. You can continue the conversation by typing further messages.
3.  **Grievance Resolution and Continuing Chat**:
    * The assistant will attempt to classify your grievance to the appropriate department. This path will be updated under "Current Department Path".
    * If the assistant indicates that a **grievance has been resolved and a new topic or grievance is introduced**, the system might automatically start a new logical session in the backend to handle the new query.
    * **Importantly, from your perspective in the chat UI, the conversation will appear to continue seamlessly.** You will see a message like, "Previous grievance has been resolved. Starting a new session," and you can continue typing in the same chat window. The chat history will persist on your screen until cleared or a new session is manually started.

## 5. Using Commands

You can type special commands in the message input field. Commands must start with a forward slash (`/`).

* **`/clear`**
    * **Usage**: `/clear`
    * **Action**: Clears the current conversation history displayed on the screen. The chat input field will be ready for a new message. This does not start a new backend session ID but reloads the current path if available.

* **`/help`**
    * **Usage**: `/help`
    * **Action**: Displays a list of available commands and their descriptions in the chat window.

* **`/get_resolved_depts`**
    * **Usage**: `/get_resolved_depts`
    * **Action**: Fetches and displays the currently resolved department path from the backend for your active session. The result will appear as an assistant message.

* **`/new_chat_sesh`**
    * **Usage**: `/new_chat_sesh`
    * **Action**: Starts a completely new chat session. This will:
        * Clear the entire conversation history from the UI.
        * Reset the "Current Department Path".
        * Obtain a new session ID from the backend.
        Use this if you want to start over with a completely unrelated query.

If you type an unknown command, the assistant will respond with an "Unknown command" message and suggest using `/help`.

## 6. Troubleshooting

* **API Connection Issues**: If the sidebar indicates an API connection error, the chat functionality may be impaired. You can try the "Force API Health Check" button. If issues persist, please notify an administrator.
* **Slow Responses**: If the assistant is taking too long to respond, it might be due to network latency or high load on the API. The interface has built-in retries for API calls. If it fails after multiple attempts, an error message will be displayed.