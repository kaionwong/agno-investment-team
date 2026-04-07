FROM agnohq/python:3.12

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# ---------------------------------------------------------------------------
# Create non-root user
# ---------------------------------------------------------------------------
RUN groupadd -g 61000 app \
    && useradd -g 61000 -u 61000 -ms /bin/bash app

# ---------------------------------------------------------------------------
# Application code
# ---------------------------------------------------------------------------
WORKDIR /app

COPY requirements.txt ./
RUN uv pip sync requirements.txt --system

# Patch agno to handle missing imports in openai 1.30.0
COPY scripts/patch_agno_openai.py /tmp/patch_agno_openai.py
RUN python /tmp/patch_agno_openai.py

COPY --chown=app:app . .

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
RUN chmod +x /app/scripts/entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["chill"]
