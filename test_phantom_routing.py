# 📄 test_phantom_routing.py
# ✅ Tests the route classification pipeline end-to-end using AzureOpenAILLM

from backend.app.routing.phantom_router import semantic_classify
import asyncio

async def main():
    task = "check compliance logs for last quarter"
    result = await semantic_classify(task)
    
    print("Route Selected:", result.name)
    print("Function Call:", result.function_call)

if __name__ == "__main__":
    asyncio.run(main())
