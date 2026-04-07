"""Test knowledge search and agent response with knowledge base."""
import sys
sys.path.insert(0, '/app')

# Test 1: Direct knowledge search
print("=== Test 1: Direct KB search ===")
from agents.settings import team_knowledge

results = team_knowledge.search("Apple AAPL company profile")
print(f"Search results count: {len(results)}")
for r in results[:2]:
    print(f"  Name: {r.name if hasattr(r, 'name') else 'N/A'}")
    content = r.content if hasattr(r, 'content') else str(r)
    print(f"  Content preview: {content[:200]}\n")

# Test 2: Another search
results2 = team_knowledge.search("NVDA Nvidia semiconductors")
print(f"\nSearch 'NVDA Nvidia': {len(results2)} results")
for r in results2[:1]:
    content = r.content if hasattr(r, 'content') else str(r)
    print(f"  Content preview: {content[:200]}")

print("\n=== Test 2: API call to knowledge-agent ===")
import requests, time

resp = requests.post(
    "http://localhost:8000/agents/knowledge-agent/runs",
    data={"message": "What does our research say about Apple (AAPL)?", "stream": "false"},
    timeout=180
)
data = resp.json()
print(f"Status: {data.get('status')}")
content = data.get("content", "")
print(f"Response preview:\n{content[:600]}")
