import asyncio
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# 1. STATE MANAGEMENT & TYPE VALIDATION (Pydantic)
# ---------------------------------------------------------
class UserQuery(BaseModel):
    """
    This defines the exact structure of the data we expect.
    Pydantic will throw an error if the data doesn't match this schema.
    """
    query: str = Field(..., description="The user's input text")
    requires_web_search: bool = Field(default=False, description="Flag for external search")

# ---------------------------------------------------------
# 2. DECORATORS
# ---------------------------------------------------------
def agent_tool(name: str):
    """
    A custom decorator that wraps around our functions. 
    It intercepts the function call to add extra behavior.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            print(f"\n[System Log] 🛠️ Spinning up tool: {name}...")
            # Run the actual function
            result = await func(*args, **kwargs)
            print(f"[System Log] ✅ Tool '{name}' executed successfully.")
            return result
        return wrapper
    return decorator

# ---------------------------------------------------------
# 3. ASYNCHRONOUS EXECUTION & TYPE HINTING
# ---------------------------------------------------------
@agent_tool(name="WebSearchTool")
async def fetch_information(state: UserQuery) -> dict:
    """
    An asynchronous function representing a tool the AI might use.
    Notice the type hint 'state: UserQuery' and the return type '-> dict'.
    """
    print(f"-> Initiating search for: '{state.query}'")
    
    # Simulate a network delay (like calling an LLM or an API)
    await asyncio.sleep(2) 
    
    # 4. Updating and returning state
    return {
        "status": "success",
        "data": f"Mock search results found for '{state.query}'",
    }

# ---------------------------------------------------------
# THE MAIN EVENT LOOP
# ---------------------------------------------------------
async def main():
    print("Initializing Agent Workflow...")
    
    # We instantiate our Pydantic model. It validates the data instantly.
    current_state = UserQuery(
        query="How to deploy a Next.js app?", 
        requires_web_search=True
    )
    
    # We 'await' the async tool, just like fetching from a database
    response = await fetch_information(current_state)
    
    print("\nFinal Agent Output:")
    print(response)

# Python's way of executing the main async function
if __name__ == "__main__":
    asyncio.run(main())