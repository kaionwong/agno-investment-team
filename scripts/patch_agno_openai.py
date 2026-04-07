#!/usr/bin/env python3
"""
Patch agno to handle missing imports in openai 1.30.0 and fix OllamaEmbedder dimensions issue
"""
import sys
import os
import re

def patch_file(file_path, old_line, new_lines):
    """Patch a Python file by replacing a line with multiple lines."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Find and replace the import line
        found = False
        for i, line in enumerate(lines):
            if old_line in line:
                # Get indentation from current line
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Create new lines with proper indentation
                patched_lines = [f"{indent_str}{nl}\n" if not nl.endswith('\n') else f"{indent_str}{nl}" 
                                 for nl in new_lines]
                
                lines[i:i+1] = patched_lines
                found = True
                break
        
        if found:
            with open(file_path, 'w') as f:
                f.writelines(lines)
            print(f"✓ Patched {file_path}")
            return True
        else:
            print(f"✗ Could not find '{old_line}' in {file_path}")
            return False
    except Exception as e:
        print(f"✗ Error patching {file_path}: {e}")
        return False

def patch_embedder_dimensions_issue():
    """Patch OllamaEmbedder to handle dimensions parameter gracefully."""
    try:
        embedder_file = '/usr/local/lib/python3.12/site-packages/agno/knowledge/embedder/ollama.py'
        with open(embedder_file, 'r') as f:
            content = f.read()
        
        # Find the embed methods and add **kwargs to absorb dimensions parameter
        # Pattern: def embed(self, input, model=...
        old_pattern = r'def embed\(self, input: str, model: str \| None = None\) -> list\[float\]:'
        new_method = 'def embed(self, input: str, model: str | None = None, **kwargs) -> list[float]:'
        
        if old_pattern in content or 'def embed(self, input:' in content:
            # More flexible replacement
            content = re.sub(
                r'def embed\(self, input: str(?:,)? model: str \| None = None\)' ,
                'def embed(self, input: str, model: str | None = None, **kwargs)',
                content
            )
            
            with open(embedder_file, 'w') as f:
                f.write(content)
            print(f"✓ Patched OllamaEmbedder to accept **kwargs")
            return True
        else:
            print(f"Could not find embed method signature in {embedder_file}")
            return False
    except Exception as e:
        print(f"Error patching embedder: {e}")
        return False

def main():
    base_path = '/usr/local/lib/python3.12/site-packages/agno/models/openai'
    
    # Patch 1: Make ChatCompletionAudio import optional in chat.py
    chat_file = f'{base_path}/chat.py'
    patch_file(chat_file, 
               'from openai.types.chat import ChatCompletion, ChatCompletionAudio, ChatCompletionChunk',
               [
                   'try:',
                   '    from openai.types.chat import ChatCompletion, ChatCompletionAudio, ChatCompletionChunk',
                   'except ImportError:',
                   '    # ChatCompletionAudio not available in older openai versions',
                   '    from openai.types.chat import ChatCompletion, ChatCompletionChunk',
                   '    class ChatCompletionAudio: pass',
               ])
    
    # Patch 2: Make openai.types.responses imports optional in responses.py
    responses_file = f'{base_path}/responses.py'
    patch_file(responses_file,
               'from openai.types.responses import Response, ResponseReasoningItem, ResponseStreamEvent, ResponseUsage',
               [
                   'try:',
                   '    from openai.types.responses import Response, ResponseReasoningItem, ResponseStreamEvent, ResponseUsage',
                   'except (ImportError, ModuleNotFoundError):',
                   '    # These types don\'t exist in older openai versions, create dummies',
                   '    class Response: pass',
                   '    class ResponseReasoningItem: pass',
                   '    class ResponseStreamEvent: pass',
                   '    class ResponseUsage: pass',
               ])
    
    # Patch 3: Fix OllamEmbedder to accept dimensions parameter
    patch_embedder_dimensions_issue()

if __name__ == '__main__':
    main()


