"""
Utility to generate quiz questions using OpenAI API.
"""

import json
import re
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv()


def generate_quiz(text_content, num_questions, difficulty):
    """
    Generate MCQ quiz questions from text content using OpenAI API.

    Args:
        text_content (str): The extracted text from slides.
        num_questions (int): Number of questions to generate (5-30).
        difficulty (str): Difficulty level - "Simple", "Medium", or "Complex".

    Returns:
        list: List of question dicts with keys:
              - question (str)
              - options (list of 4 str)
              - correct_answer (str)
              - explanation (str)
    """
    if not text_content or text_content.strip() == "":
        raise ValueError("No text content provided for quiz generation.")

    if num_questions < 5 or num_questions > 30:
        raise ValueError("Number of questions must be between 5 and 30.")

    valid_difficulties = ["Simple", "Medium", "Complex"]
    if difficulty not in valid_difficulties:
        raise ValueError(f"Difficulty must be one of: {', '.join(valid_difficulties)}")

    api_key = _get_api_key()
    client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

    difficulty_instructions = {
        "Simple": "Focus on basic recall, definitions, and fundamental concepts from the text. Questions should be straightforward and test surface-level understanding.",
        "Medium": "Test comprehension and application of concepts. Include questions that require understanding relationships between ideas and moderate analytical thinking.",
        "Complex": "Test deep understanding, synthesis, and critical analysis. Include questions that require combining multiple concepts, evaluating scenarios, and applying knowledge in new contexts."
    }

    prompt = f"""You are a quiz generation expert. Based on the following text content, generate exactly {num_questions} multiple-choice questions (MCQs).

Difficulty Level: {difficulty}
{difficulty_instructions[difficulty]}

Text Content:
{text_content[:12000]}  # Limit text to avoid token limits

For each question, provide:
1. A clear question
2. Four options (A, B, C, D)
3. The correct answer (must be one of the four options verbatim)
4. A detailed explanation of why the answer is correct

Return ONLY a valid JSON array (no markdown formatting, no code blocks). Each object in the array must have these exact keys:
- "question": string
- "options": array of 4 strings
- "correct_answer": string (must exactly match one of the options)
- "explanation": string

Example format:
[
  {{
    "question": "What is the capital of France?",
    "options": ["London", "Paris", "Berlin", "Madrid"],
    "correct_answer": "Paris",
    "explanation": "Paris is the capital and most populous city of France."
  }}
]

Generate exactly {num_questions} questions. Ensure each question is unique and directly based on the provided text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful quiz generator that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )

        content = response.choices[0].message.content.strip()
        questions = _parse_response(content, num_questions)
        return questions

    except Exception as e:
        raise RuntimeError(f"Failed to generate quiz: {str(e)}")


def _get_api_key():
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Create a .env file in the project root with:\n\nOPENAI_API_KEY=your_api_key"
        )

    return api_key


def _parse_response(content, expected_count):
    """Parse the JSON response from OpenAI."""
    # Try to extract JSON from the response (handle markdown code blocks)
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
    if json_match:
        content = json_match.group(1)

    content = content.strip()

    try:
        questions = json.loads(content)
    except json.JSONDecodeError:
        # Try to fix common issues
        content = content.replace("'", '"')
        try:
            questions = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse quiz response as JSON. Raw response:\n{content[:500]}"
            ) from e

    if not isinstance(questions, list):
        raise ValueError("Response is not a JSON array.")

    # Validate each question
    validated = []
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            continue
        if "question" not in q or "options" not in q or "correct_answer" not in q or "explanation" not in q:
            continue
        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            continue
        if q["correct_answer"] not in q["options"]:
            continue
        validated.append(q)

    if len(validated) < expected_count:
        # If we got fewer questions than expected, that's okay but warn
        pass

    if not validated:
        raise ValueError("No valid questions could be parsed from the response.")

    return validated