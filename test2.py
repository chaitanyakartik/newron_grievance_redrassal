from utils.chat_utils import query_classifier, History
import asyncio

# Example history list using the History class
example_history = [
    History(role="user", content="I have a prpoblem with my room"),
    History(role="assistant", content="What specifically is the problem with your room?  Is it related to cleanliness, maintenance, facilities, or something else?"),
]

async def main():
    result = await query_classifier(
        query="I submitted my application for the Kisan Samman Nidhi Scheme through the CSC Center however, it has yet to receive approval from the Karnataka state government. Could you kindly verify and confirm our details?",
        history=example_history,
        dept_path=[]
    )
    print(result)

asyncio.run(main())