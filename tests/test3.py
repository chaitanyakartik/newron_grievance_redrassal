import uuid
import os
import json
import asyncio  # Add this import
from utils.chat_utils2 import (
    agriculture_tree,
    get_next_children as get_next_children_names,
    update_dept_path,
    check_if_final_department
)

async def test_update_dept_path():
    """Test the update_dept_path function by creating a session and updating its path."""
    # Generate a random session ID
    session_id = "69ca6c42-0f2e-4e05-8447-825902428c64"
    print(f"Testing update_dept_path with session ID: {session_id}")
    
    # Test with different department paths
    paths_to_test = [
        ["AGRICULTURE DEPARTMENT"],
        ["AGRICULTURE DEPARTMENT", "DEPARTMENT OF AGRICULTURE"],
        ["AGRICULTURE DEPARTMENT", "DEPARTMENT OF AGRICULTURE", "PM-KISAN- DISBURSEMENT OF FINANCIALL ASSISTANCE TO THE FARMERS FOR PURCHASE OF AGRI-INPUTS."],
        ["AGRICULTURE DEPARTMENT", "DEPARTMENT OF AGRICULTURE", "PM-KISAN- DISBURSEMENT OF FINANCIALL ASSISTANCE TO THE FARMERS FOR PURCHASE OF AGRI-INPUTS.", "ISSUES RELATED TO APPLICATION"]
    ]
    
    for path in paths_to_test:
        await update_dept_path(session_id, path)
        print(f"Updated path: {path}")
        
        # Verify the update by reading the file directly
        file_path = f"chat_history/{session_id}.json"
        with open(file_path, "r") as file:
            session_data = json.load(file)
            assert session_data["current_path"] == path, f"Path mismatch: {session_data['current_path']} != {path}"
            print(f"Verification successful: {session_data['current_path']}")

async def test_check_if_final_department():
    """Test the check_if_final_department function with various paths."""
    print("\nTesting check_if_final_department function:")
    
    # Test cases: (path, expected_result)
    test_cases = [
        # Not final
        ([], False),
        (["AGRICULTURE DEPARTMENT"], False),
        (["AGRICULTURE DEPARTMENT", "DEPARTMENT OF AGRICULTURE"], False),

        # Final/leaf nodes (should be True)
        (
            ["AGRICULTURE DEPARTMENT", "DEPARTMENT OF AGRICULTURE", "EMPLOYEE BENEFIT", "FACING ISSUES RELATED TO EMPLOYEE BENEFITS", "ISSUE RELATED TO ESI"],
            True
        ),
        (
            ["AGRICULTURE DEPARTMENT", "DEPARTMENT OF AGRICULTURE", "KARNATAKA CROP SURVEY- TO CAPTURE THE DETAILS OF CROPS GROWN BY THE FARMING COMMUNITY", "ISSUES RELATED TO APPLICATION", "APPLICATION HAS BEEN SUBMITTED BUT NOT PROCESSED"],
            True
        ),
        (
            ["AGRICULTURE DEPARTMENT", "KARNATAKA STATE SEEDS CORPORATION LIMITED", "PRODUCTION AND DISTRIBUTION OF GOOD SEEDS TO THE  STATE OF FARMERS", "ISSUES RELATED TO PRODUCTION AND DISTRIBUTION OF GOOD SEEDS TO THE STATE FARMERS", "GENERAL"],
            True
        ),
        (
            ["AGRICULTURE DEPARTMENT", "AGRICULTURAL UNIVERSITIES", "EMPLOYEE BENEFIT", "FACING ISSUES RELATED TO EMPLOYEE BENEFITS", "ISSUE RELATED TO PF"],
            True
        ),
        # Not found/invalid
        (["AGRICULTURE DEPARTMENT", "NOT A REAL DEPARTMENT"], False),
    ]
    
    for path, expected in test_cases:
        result = await check_if_final_department(path)
        print(f"Path: {path}")
        print(f"Expected: {expected}, Got: {result}")
        assert result == expected, f"Failed: Expected {expected}, got {result} for {path}"
        print("✓ Test passed\n")

async def test_next_children_names():
    """Test the get_next_children_names function with various paths."""
    print("\nTesting get_next_children_names function:")
    
    # Test cases: paths to check
    test_paths = [
        [],
        ["AGRICULTURE DEPARTMENT"],
        ["AGRICULTURE DEPARTMENT", "DEPARTMENT OF AGRICULTURE"],
        # Add more test paths as needed
    ]
    
    for path in test_paths:
        children = await get_next_children_names(agriculture_tree, path)
        print(f"Path: {path}")
        print(f"Children: {children}")
        print(f"Number of children: {len(children)}")
        print("------------------------")

async def main():
    """Run all tests."""
    print("Starting tests...\n")
    
    # Run all tests
    # await test_update_dept_path()
    await test_check_if_final_department()
    # await test_next_children_names()
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    # Use asyncio.run() to run the main async function
    asyncio.run(main())