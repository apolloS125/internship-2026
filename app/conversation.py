MAX_HISTORY_MESSAGES = 10

conversations = {}

def get_history(conversation_id):
    return conversations.get(conversation_id, []).copy()

def add_turn(conversation_id, user_message, assistant_message):
    history = conversations.setdefault(conversation_id, [])
    history.extend(
        [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ]
    )
    conversations[conversation_id] = history[-MAX_HISTORY_MESSAGES:]

def make_search_query(message, history):
    for item in reversed(history):
        if item["role"] == "user":
            return f"{item['content']}\n{message}"

    return message

def clear_history(conversation_id):
    conversations.pop(conversation_id, None)
