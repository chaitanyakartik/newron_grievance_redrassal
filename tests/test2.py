from utils.chat_utils import query_classifier, History
import asyncio
        
        
query="I submitted my application for the Kisan Samman Nidhi Scheme through the CSC Center however, it has yet to receive approval from the Karnataka state government. Could you kindly verify and confirm our details?",
query1="i have a problem with my application process, agricutlure realted, related to crop survey"
async def main():
    result, path = await query_classifier(
        query=query1,
        chat_session_id="69ca6c42-0f2e-4e05-8447-825902428c64"
    )
    print(result)
    print(path)

asyncio.run(main())

