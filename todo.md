# TODO - Known Issues & Resolutions

## 🚨 CRITICAL: Knowledge Base Embedding Dimension Mismatch

**Status:** Unresolved - Blocking knowledge base initialization

### Problem
When running `docker exec -it investment-team-api python -m app.load_knowledge`, documents fail to load with:
```
WARNING  Client.embed() got an unexpected keyword argument 'dimensions'
ERROR    Error upserting document: (builtins.ValueError) expected 4096 dimensions, not 0
```

The OllamaEmbedder returns 0-dimensional vectors, causing all 9 research documents to fail insertion into the pgvector database.

### Root Cause
Incompatibility between **agno 2.5.x** and **openai 1.30.0** when calling the embedding service:
- agno is passing a `dimensions` parameter to the embedder
- openai 1.30.0 doesn't support this parameter in the old API style
- OllamaEmbedder doesn't know how to handle the unexpected parameter
- Result: empty/0-dimensional embeddings that pgvector rejects

### What's Been Tried (Failed)

1. **Openai Version Experiments** (10+ versions tested):
   - 1.30.0 → Incompatible embedding call
   - 1.47.0 → Same embedding error
   - 1.54.0 → Same embedding error
   - 1.59.3 → Same embedding error
   - 2.30.0 → ChatCompletionAudio import errors
   - Various others (0.28.0, 1.3.0, 1.50.0, etc.)

2. **Agno Version Changes**:
   - 2.5.2 → import failures
   - 2.5.0 → embedding dimension errors
   - 2.5.13 → embedding dimension errors

3. **Search Type Changes**:
   - Hybrid search → embedding errors
   - Keyword-only search → embedding errors  
   - No embedder specified → still generates embeddings that fail

4. **Patching Strategies**:
   - Monkey-patched agno imports → helps imports but not embeddings
   - Docker-layer patches for ChatCompletionAudio → works but doesn't fix embeddings
   - Attempted OllamaEmbedder signature modification → signature not found

### Current System State

✅ **Working:**
- Docker containers running (API + PostgreSQL)
- API server operational on `localhost:8000`
- Database initialized with pgvector support
- All 7 agents and 4 teams deployed
- Patches applied for openai import compatibility

❌ **Not Working:**
- Knowledge base load fails on all 9 documents
- 0 documents in `ai.team_knowledge` table
- Embedding dimension validation fails at pgvector layer

### Workarounds Available

1. **Use Agents Without Knowledge Base**:
   - Market Analyst uses Exa + YFinance (doesn't need knowledge base)
   - Financial Analyst uses YFinance (doesn't need knowledge base)
   - Technical Analyst uses YFinance (doesn't need knowledge base)
   - Risk Officer uses YFinance (doesn't need knowledge base)
   - System is fully functional for queries without RAG

2. **Test API Without Knowledge**:
   - Connect to UI at https://os.agno.com
   - Query individual agents for financial data
   - Full functionality except knowledge-based research queries

### Recommended Solutions

**Short term (use now):**
- Skip knowledge base initialization for immediate functionality
- Use built-in tools (Exa, YFinance) for all agent operations
- Agents still provide full value without RAG layer

**Medium term (could work):**
1. Check Agno GitHub issues for openai compatibility discussions
2. Try latest agno version (2.5.13+) with explicit version constraint for openai
3. Contact Agno support for embedding parameter compatibility guidance
4. Investigate if there's a configuration flag to disable dimensions parameter

**Long term (permanent fix):**
1. Wait for agno or openai to release compatible versions
2. Switch to a different embedding provider if available
3. Implement custom wrapper around OllamaEmbedder to handle parameter mismatch

### Files Modified

- `db/session.py` - Changed from hybrid search with embedder to keyword-only
- `pyproject.toml` - Pinned agno 2.5.0, openai 1.30.0
- `requirements.txt` - Matching versions
- `Dockerfile` - Added patch script for import compatibility
- `scripts/patch_agno_openai.py` - Patches for openai import errors
- `app/main.py` - Monkey-patch attempt (partial fix)
- `app/load_knowledge.py` - Monkey-patch attempt (partial fix)

### Testing Commands

```powershell
# Check knowledge base status
docker exec investment-team-db psql -U postgres -d agno_investment_team -c "SELECT COUNT(*) FROM ai.team_knowledge"

# View API logs
docker logs -f investment-team-api

# Test knowledge loading
docker exec -it investment-team-api python -m app.load_knowledge

# Try without knowledge base
$env:SKIP_KNOWLEDGE_LOAD=true; docker exec -it investment-team-api python -m app.main
```

### Next Step If Revisiting

1. Create minimal reproduction: separate test script that calls OllamaEmbedder directly
2. Trace the dimensions parameter source in agno codebase
3. Check if there's a feature flag or configuration to disable it
4. Consider forking agno to apply fix locally

---

**Last Updated:** April 5, 2026  
**Triage:** This is blocking knowledge-based RAG queries but not core agent functionality
