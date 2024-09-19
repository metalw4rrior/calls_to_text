# database.py
import asyncpg
import asyncio
async def init_db():
    return await asyncpg.connect(
        user='user',
        password='pass',
        database='db',
        host='host',
        port='6432',
        statement_cache_size=0
    )

async def check_file_existence(conn, filename):
    query = "SELECT COUNT(*) FROM incoming_calls WHERE filename LIKE $1"
    return await conn.fetchval(query, filename)

async def save_transcription(conn, call_type, filename, phone_number, operator_number, call_date, call_time, corrected_transcription, is_correct, result, dialogue_count):
    if call_type == "in":
        await conn.execute('''
            INSERT INTO incoming_calls(filename, phone_number, operator_number, call_date, call_time, transcript, is_corrected, result, dialogue_count) 
            VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ''', filename, phone_number, operator_number, call_date, call_time, corrected_transcription, is_correct, result, dialogue_count)
    elif call_type == "out":
        await conn.execute('''
            INSERT INTO outgoing_calls(filename, phone_number, operator_number, call_date, call_time, transcript, is_corrected, result, dialogue_count) 
            VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ''', filename, phone_number, operator_number, call_date, call_time, corrected_transcription, is_correct, result, dialogue_count)




async def get_keywords_with_categories_from_db(conn):
    """
    Fetch keywords and their corresponding categories from the database.
    """
    async with conn.transaction():
        rows = await conn.fetch("""
            SELECT c.name AS category, k.keyword 
            FROM keywords k
            JOIN categories c ON k.category_id = c.id
        """)
        keywords_with_categories = {}
        for row in rows:
            category = row['category'].lower()
            keyword = row['keyword'].lower()
            if category not in keywords_with_categories:
                keywords_with_categories[category] = []
            keywords_with_categories[category].append(keyword)
    return keywords_with_categories





async def get_call_keywords_with_categories_from_db(conn):
    query = """
        SELECT cp.text AS keyword, cc.id AS category_id
        FROM category_phrases cp
        JOIN call_categories cc ON cp.category_id = cc.id;
    """
    result = await conn.fetch(query)
    keywords_with_categories = {}
    for row in result:
        keyword, category_id = row['keyword'], row['category_id']
        if category_id not in keywords_with_categories:
            keywords_with_categories[category_id] = []
        keywords_with_categories[category_id].append(keyword.lower())
    return keywords_with_categories


import logging
async def get_assigned_operators_with_keywords(conn, operator_name):
    query = """
        SELECT co.id AS operator_id, co.operator_name AS operator_name, cp.text AS keyword
        FROM call_category_operator cco
        JOIN call_operators co ON cco.operator_id = co.id
        JOIN category_phrases cp ON cco.category_id = cp.category_id
        WHERE co.operator_name ILIKE $1;
    """
    try:
        result = await conn.fetch(query, operator_name)
        logging.info(f"Fetched {len(result)} rows for operator '{operator_name}'")
        
        assigned_operators_with_keywords = {}
        for row in result:
            operator_id, operator_name, keyword = row
            if operator_id not in assigned_operators_with_keywords:
                assigned_operators_with_keywords[operator_id] = {'name': operator_name, 'keywords': []}
            assigned_operators_with_keywords[operator_id]['keywords'].append(keyword.lower())

        logging.info(f"Operators with keywords: {assigned_operators_with_keywords}")
        return assigned_operators_with_keywords

    except Exception as e:
        logging.error(f"Error fetching operators with keywords: {e}")
        raise
