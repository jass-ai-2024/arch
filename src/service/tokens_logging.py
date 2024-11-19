from functools import wraps
from typing import Any, Callable, Dict
import tiktoken
from datetime import datetime

def count_tokens(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Get messages from kwargs or first arg if it's a list
        messages = kwargs.get('messages') or (args[0] if args else None)
        if not messages:
            return func(*args, **kwargs)

        # Initialize tokenizer
        encoding = tiktoken.encoding_for_model("gpt-4o")
        
        # Count tokens in messages
        token_count = 0
        for message in messages:
            token_count += len(encoding.encode(message.get("content", "")))
        
        # Execute the original function
        response = func(*args, **kwargs)
        
        # Count tokens in the response
        if response and hasattr(response, 'messages'):
            for message in response.messages:
                token_count += len(encoding.encode(message.get("content", "")))
        
        # Log token usage
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] Total tokens used: {token_count}")
        
        return response
    return wrapper
