#!/usr/bin/env python3
"""
Prompt Tester for Claude Opus 4.5

This program tests the efficacy of a system prompt by comparing Claude's responses
to test cases with and without the prompt.

Input files (place in same directory as this script):
  - prompt.txt: Your system prompt (the prompt that changes behavior)
  - test_cases.txt: 10 test cases, one per line

Output:
  - output.csv: CSV file with columns matching the Anthropic application template

Usage:
  1. Set your API key in the ANTHROPIC_API_KEY variable below (or as environment variable)
  2. Create prompt.txt with your system prompt
  3. Create test_cases.txt with 10 test cases (one per line)
  4. Run: python prompt_tester.py
"""

import os
import csv
import time
from pathlib import Path

# =============================================================================
# CONFIGURATION - Set your API key here or as an environment variable
# =============================================================================
# Option 1: Set directly (replace with your actual key)
ANTHROPIC_API_KEY = "YOUR_API_KEY_HERE"  # <-- Replace this with your actual API key

# Option 2: Or set as environment variable ANTHROPIC_API_KEY and leave the above as-is
# The program will check the environment variable if the above is not set
# =============================================================================

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed.")
    print("Please install it with: pip install anthropic")
    exit(1)


def get_api_key() -> str:
    """Get API key from config or environment variable."""
    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "YOUR_API_KEY_HERE":
        return ANTHROPIC_API_KEY

    env_key = os.environ.get("ANTHROPIC_API_KEY")
    if env_key:
        return env_key

    print("Error: No API key found.")
    print("Please either:")
    print("  1. Set ANTHROPIC_API_KEY in this script")
    print("  2. Set ANTHROPIC_API_KEY environment variable")
    exit(1)


def get_script_dir() -> Path:
    """Get the directory where this script is located."""
    return Path(__file__).parent.resolve()


def read_prompt(script_dir: Path) -> str:
    """Read the system prompt from prompt.txt."""
    prompt_file = script_dir / "prompt.txt"
    if not prompt_file.exists():
        print(f"Error: {prompt_file} not found.")
        print("Please create prompt.txt with your system prompt.")
        exit(1)

    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read().strip()


def read_test_cases(script_dir: Path) -> list[str]:
    """Read test cases from test_cases.txt (one per line)."""
    test_cases_file = script_dir / "test_cases.txt"
    if not test_cases_file.exists():
        print(f"Error: {test_cases_file} not found.")
        print("Please create test_cases.txt with 10 test cases (one per line).")
        exit(1)

    with open(test_cases_file, "r", encoding="utf-8") as f:
        cases = [line.strip() for line in f if line.strip()]

    if len(cases) == 0:
        print("Error: test_cases.txt is empty.")
        exit(1)

    if len(cases) != 10:
        print(f"Warning: Expected 10 test cases, found {len(cases)}. Continuing anyway.")

    return cases


def call_claude(
    client: anthropic.Anthropic,
    user_message: str,
    system_prompt: str | None = None
) -> str:
    """
    Make a single API call to Claude Opus 4.5.

    Args:
        client: Anthropic client instance
        user_message: The user's message/test case
        system_prompt: Optional system prompt (None for no system prompt)

    Returns:
        Claude's response text
    """
    model = "claude-opus-4-5-20250514"

    kwargs = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": user_message}]
    }

    if system_prompt:
        kwargs["system"] = system_prompt

    try:
        response = client.messages.create(**kwargs)
        # Extract text from response
        if response.content and len(response.content) > 0:
            return response.content[0].text
        return ""
    except anthropic.APIError as e:
        return f"[API Error: {e}]"


def main():
    print("=" * 60)
    print("Prompt Tester for Claude Opus 4.5")
    print("=" * 60)

    # Setup
    script_dir = get_script_dir()
    api_key = get_api_key()
    client = anthropic.Anthropic(api_key=api_key)

    # Read inputs
    print("\nReading input files...")
    system_prompt = read_prompt(script_dir)
    test_cases = read_test_cases(script_dir)

    print(f"  - System prompt: {len(system_prompt)} characters")
    print(f"  - Test cases: {len(test_cases)} cases")

    # Prepare results storage
    results = []

    # Process each test case
    total_calls = len(test_cases) * 2
    current_call = 0

    print(f"\nMaking {total_calls} API calls to Claude Opus 4.5...")
    print("(This may take a few minutes)\n")

    for i, test_case in enumerate(test_cases):
        print(f"Test case {i + 1}/{len(test_cases)}: {test_case[:50]}{'...' if len(test_case) > 50 else ''}")

        # Call without system prompt
        current_call += 1
        print(f"  [{current_call}/{total_calls}] Without system prompt...", end=" ", flush=True)
        response_without = call_claude(client, test_case, system_prompt=None)
        print("Done")

        # Small delay to avoid rate limiting
        time.sleep(0.5)

        # Call with system prompt
        current_call += 1
        print(f"  [{current_call}/{total_calls}] With system prompt...", end=" ", flush=True)
        response_with = call_claude(client, test_case, system_prompt=system_prompt)
        print("Done")

        # Store result
        results.append({
            "prompt": system_prompt,
            "test_case": test_case,
            "output_without_prompt": response_without,
            "output_with_prompt": response_with
        })

        # Small delay between test cases
        if i < len(test_cases) - 1:
            time.sleep(0.5)

    # Write output CSV
    output_file = script_dir / "output.csv"
    print(f"\nWriting results to {output_file}...")

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        # Header matching the Google Sheet template
        writer.writerow([
            "prompt",
            "test_case",
            "Claude's output (no system prompt)",
            "Claude's output (with your prompt)"
        ])

        # Data rows
        for result in results:
            writer.writerow([
                result["prompt"],
                result["test_case"],
                result["output_without_prompt"],
                result["output_with_prompt"]
            ])

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print(f"\nOutput saved to: {output_file}")
    print("\nYou can now:")
    print("  1. Open the CSV in a spreadsheet application")
    print("  2. Copy the data into your Google Sheet submission")
    print("  3. Review the differences between responses with/without your prompt")


if __name__ == "__main__":
    main()
