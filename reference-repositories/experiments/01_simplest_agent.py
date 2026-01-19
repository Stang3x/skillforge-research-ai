from anthropic import Anthropic

client = Anthropic()

# Single interaction - not even a loop yet
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is 5 + 3?"}]
)

print(response.content[0].text)
