def count_tokens_mock(text: str) -> int:
    # Lightweight token estimate: words as tokens (fast approximation)
    return max(1, len(text.split()))

def calculate_cost(tokens: int, price_per_million: float) -> float:
    return (tokens / 1_000_000) * price_per_million
