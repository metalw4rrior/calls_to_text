import asyncio
from database import init_db, get_keywords_with_categories_from_db, get_assigned_operators_with_keywords

async def analyze_dialogue(transcript, operator_name):
    conn = await init_db()
    try:
        # Fetch data
        keywords_with_categories = await get_keywords_with_categories_from_db(conn)
        assigned_operators_with_keywords = await get_assigned_operators_with_keywords(conn, operator_name)

        # Clean and split transcript
        transcript = transcript.replace('\t', '').replace('}', '\n').replace('{', '').strip()
        dialogues = [line.strip() for line in transcript.split('\n') if line.strip()]

        # Helper function to check if any keyword is present in the text
        def contains_any(keywords, text):
            return any(keyword in text.lower() for keyword in keywords)

        # Initialize variables
        category_found = "???"
        is_corrected = False

        # Check for categories
        for category, keywords in keywords_with_categories.items():
            if any(contains_any(keywords, phrase) for phrase in dialogues):
                category_found = category
                break  # Found a category, no need to check further

        # Check for operator keywords if operator is found
        if operator_name in [data['name'] for data in assigned_operators_with_keywords.values()]:
            for operator_id, data in assigned_operators_with_keywords.items():
                if data['name'].lower() == operator_name.lower():
                    operator_keywords = data['keywords']

                    if any(contains_any(operator_keywords, phrase) for phrase in dialogues):
                        is_corrected = True
                        break  # No need to check further if keywords are found

        return category_found, len(dialogues), is_corrected

    finally:
        await conn.close()
