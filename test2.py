from utils.chat_utils import query_classifier, History
import asyncio

# Example history list using the History class
example_history = [
    History(role="user", content="I have a prpoblem with my room"),
    History(role="assistant", content="What specifically is the problem with your room?  Is it related to cleanliness, maintenance, facilities, or something else?"),
]

async def main():
    result = await query_classifier(
        query="its reguarding payment",
        history=example_history,
        dept_path=[]
    )
    print(result)

asyncio.run(main())
