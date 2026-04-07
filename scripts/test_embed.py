"""Test Ollama embed API directly."""
import sys
sys.path.insert(0, '/app')
import ollama

client = ollama.Client(host='http://host.docker.internal:11434')
result = client.embed(input='test embedding', model='nomic-embed-text')

print(f"Result type: {type(result)}")
print(f"Result keys: {list(result.keys()) if hasattr(result, 'keys') else 'N/A'}")

if 'embeddings' in result:
    embeddings = result['embeddings']
    if embeddings and isinstance(embeddings[0], list):
        print(f"Embedding dims (nested): {len(embeddings[0])}")
    elif embeddings:
        print(f"Embedding dims (flat): {len(embeddings)}")
    else:
        print("Embeddings empty")
elif 'embedding' in result:
    print(f"Embedding dims (singular): {len(result['embedding'])}")
else:
    print(f"Full result: {result}")
