---
name: doc-classifier
type: tool
description: 'Auto-detects document type from file path or content with confidence
  scoring, trying path-based detection first then content analysis

  '
version: 1.0.0
parameters:
  type: object
  properties:
    operation:
      type: string
    parameters:
      type: object
implementation:
  type: bash
  scripts_directory: scripts
llm:
  model: claude-haiku-4-5
---

# doc-classifier

<CONTEXT>
**Purpose**: Auto-detect doc_type from file path or content.

**Strategy**:
1. Path pattern first (docs/api/ → api)
2. Content analysis fallback (read fractary_doc_type from frontmatter)
</CONTEXT>

<CRITICAL_RULES>
- ALWAYS try path-based detection first
- ONLY read file if path detection fails
- NEVER modify files
- ALWAYS return confidence score (0-100)
</CRITICAL_RULES>

<INPUTS>
- `file_path` OR `content` (one required)
</INPUTS>

<WORKFLOW>
1. **Path-Based Detection**
   - Check if path matches: docs/{doc_type}/
   - Return doc_type with confidence 100

2. **Content-Based Detection**
   - Read file (if file_path) or use content
   - Extract frontmatter
   - Read `fractary_doc_type` field
   - Return with confidence 90

3. **Fallback**
   - Return `_untyped` with confidence 50
</WORKFLOW>

<OUTPUTS>
```json
{
  "doc_type": "api",
  "confidence": 100,
  "method": "path|frontmatter|fallback"
}
```
</OUTPUTS>
