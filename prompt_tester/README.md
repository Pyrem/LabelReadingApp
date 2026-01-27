# Prompt Tester for Claude Opus 4.5

A tool for testing the efficacy of system prompts by comparing Claude's responses with and without the prompt.

## Setup

1. Install the required dependency:
   ```bash
   pip install anthropic
   ```

2. Set your Anthropic API key (choose one method):
   - **Option A**: Edit `prompt_tester.py` and replace `YOUR_API_KEY_HERE` with your actual key
   - **Option B**: Set environment variable:
     ```bash
     export ANTHROPIC_API_KEY="your-api-key-here"
     ```

## Usage

1. Edit `prompt.txt` with your system prompt (the prompt that changes behavior)

2. Edit `test_cases.txt` with 10 test cases, one per line

3. Run the program:
   ```bash
   python prompt_tester.py
   ```

4. Results will be saved to `output.csv`

## Output Format

The CSV output matches the Anthropic application template:

| Column | Description |
|--------|-------------|
| prompt | Your system prompt (same for all rows) |
| test_case | The user message/test case |
| Claude's output (no system prompt) | Response without any system prompt |
| Claude's output (with your prompt) | Response with your system prompt |

## Notes

- Each API call is completely independent (fresh conversation)
- Uses Claude Opus 4.5 model (`claude-opus-4-5-20250514`)
- Standard parameters (temperature default, 4096 max tokens)
- Small delays between calls to avoid rate limiting
