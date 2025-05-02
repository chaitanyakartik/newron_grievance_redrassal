from utils.chat_utils import query_classifier, History
import asyncio

# Example history list using the History class
example_history = [
    History(role="user", content="I have a prpoblem with my room"),
    History(role="assistant", content="What specifically is the problem with your room?  Is it related to cleanliness, maintenance, facilities, or something else?"),
]

history=[]

async def main():
    # history = example_history.copy()
    dept_path = []
    print("Type 'exit' to quit the chat.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        history.append(History(role="user", content=user_input))
        result = await query_classifier(
            query=user_input,
            history=history,
            dept_path=dept_path
        )
        print(f"Assistant: {result}")
        history.append(History(role="assistant", content=str(result)))

asyncio.run(main())