#!/usr/bin/env python3
"""
Test script to compare token counting methods:
Level 1 (approximation) vs Level 2 (accurate API)
"""

import sys
from anthropic import Anthropic

# Initialize client
ANTHROPIC_API_KEY = "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"
client = Anthropic(api_key=ANTHROPIC_API_KEY)


def count_tokens_approximation(messages):
    """Method 1: Character approximation (4 chars = 1 token)"""
    total_chars = sum(len(msg["content"]) for msg in messages)
    return total_chars // 4


def count_tokens_accurate(messages):
    """Method 2: Anthropic count_tokens API"""
    try:
        response = client.messages.count_tokens(
            model="claude-sonnet-4-5",
            messages=messages
        )
        return response.input_tokens
    except Exception as e:
        print(f"Error: {e}")
        return None


# Test cases
test_cases = [
    {
        "name": "Short conversation",
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
    },
    {
        "name": "Medium conversation",
        "messages": [
            {"role": "user", "content": "What is machine learning?"},
            {"role": "assistant", "content": "Machine learning is a subset of artificial intelligence that focuses on developing systems that can learn from and make decisions based on data."}
        ]
    },
    {
        "name": "Long technical conversation",
        "messages": [
            {"role": "user", "content": "Can you explain how transformer models work in natural language processing?"},
            {"role": "assistant", "content": "Transformer models are a type of neural network architecture that revolutionized NLP. They use self-attention mechanisms to process input sequences in parallel, unlike RNNs which process sequentially. The key components are: 1) Multi-head self-attention layers that learn relationships between all tokens in a sequence, 2) Position encodings to capture word order, 3) Feed-forward networks, and 4) Layer normalization. This architecture enables models like BERT and GPT to achieve state-of-the-art performance on various language tasks."},
            {"role": "user", "content": "How does self-attention work exactly?"},
            {"role": "assistant", "content": "Self-attention works by computing attention scores between every pair of tokens in a sequence. For each token, it creates three vectors: Query (Q), Key (K), and Value (V). The attention score is calculated by taking the dot product of Q and K, scaling it, then applying softmax to get weights. These weights are multiplied by V to produce the output. This allows each token to 'attend' to all other tokens, capturing long-range dependencies efficiently."}
        ]
    },
    {
        "name": "Code-heavy conversation",
        "messages": [
            {"role": "user", "content": "Write a Python function to calculate fibonacci numbers"},
            {"role": "assistant", "content": "Here's a Python function:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n```"}
        ]
    },
    {
        "name": "Multi-turn research",
        "messages": [
            {"role": "user", "content": "What are the key differences between supervised and unsupervised learning?"},
            {"role": "assistant", "content": "Supervised learning uses labeled data where both input and output are known, training models to predict outputs for new inputs. Examples: classification, regression. Unsupervised learning works with unlabeled data, finding patterns and structure. Examples: clustering, dimensionality reduction."},
            {"role": "user", "content": "Can you give me real-world examples of each?"},
            {"role": "assistant", "content": "Supervised: Email spam detection (labeled emails), house price prediction (historical sales data), medical diagnosis (labeled patient records). Unsupervised: Customer segmentation (grouping similar customers), anomaly detection (finding unusual patterns), recommendation systems (identifying similar items)."},
            {"role": "user", "content": "Which one is more commonly used in production?"},
            {"role": "assistant", "content": "Supervised learning is more common in production due to clear metrics and evaluation. However, unsupervised learning is growing, especially for: customer analytics, fraud detection, and data preprocessing. Many production systems combine both approaches."}
        ]
    }
]


def run_tests():
    """Run all test cases and display results"""
    print("="*80)
    print("TOKEN COUNTING ACCURACY TEST")
    print("="*80)
    print("\nComparing Level 1 (approximation) vs Level 2 (accurate API)\n")

    total_approx = 0
    total_accurate = 0
    errors = []

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print("-" * 60)

        # Method 1: Approximation
        approx = count_tokens_approximation(test['messages'])
        print(f"Approximation (4 chars = 1 token):  {approx:4d} tokens")

        # Method 2: Accurate
        accurate = count_tokens_accurate(test['messages'])
        if accurate is not None:
            print(f"Accurate (Anthropic API):           {accurate:4d} tokens")

            # Calculate difference
            difference = accurate - approx
            percent_diff = (abs(difference) / accurate * 100) if accurate > 0 else 0

            print(f"Difference:                         {difference:+4d} tokens ({percent_diff:.1f}%)")

            if abs(percent_diff) > 20:
                errors.append(f"Test {i}: {percent_diff:.1f}% difference")

            total_approx += approx
            total_accurate += accurate
        else:
            print(f"Accurate (Anthropic API):           ERROR")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total messages tested: {len(test_cases)}")
    print(f"Total approximated tokens: {total_approx}")
    print(f"Total accurate tokens: {total_accurate}")

    if total_accurate > 0:
        overall_diff = total_accurate - total_approx
        overall_percent = (abs(overall_diff) / total_accurate * 100)
        print(f"Overall difference: {overall_diff:+d} tokens ({overall_percent:.1f}%)")

    if errors:
        print(f"\nHigh error cases (>20% difference):")
        for error in errors:
            print(f"  - {error}")
    else:
        print(f"\n[OK] All tests within 20% accuracy threshold")

    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)

    if overall_percent < 10:
        print("[OK] Approximation is HIGHLY ACCURATE (<10% error)")
        print("  Recommendation: Use approximation for low-latency applications")
    elif overall_percent < 20:
        print("[OK] Approximation is REASONABLY ACCURATE (<20% error)")
        print("  Recommendation: Use approximation for most use cases, accurate for critical apps")
    else:
        print("[ERROR] Approximation has SIGNIFICANT ERROR (>20%)")
        print("  Recommendation: Always use accurate API counting")

    print("\nKey Insights:")
    print("  - Approximation is INSTANT (0ms latency)")
    print("  - Accurate API adds ~50-200ms per count")
    print(f"  - For {len(test_cases)} tests, API made {len(test_cases)} calls")
    print("  - Approximation works best for ASCII text")
    print("  - Code, special characters, and emojis increase error")


if __name__ == "__main__":
    run_tests()
