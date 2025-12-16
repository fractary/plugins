# Consolidated Requirements for Fractary Registry and Plugin Conversion

**Date:** 2025-12-15
**Repository:** `fractary/plugins` (copy of `fractary/claude-plugins`)
**Status:** Confirmed

## Executive Summary

Based on analysis of the three specifications, the **current and correct approach** is defined by **SPEC-FORGE-005** and **SPEC-FORGE-007**. The initial plan in FORGE-PHASE-3B has been superseded by the registry manifest system approach.

## Confirmed: Work Location

✅ **YES - All work should be done in the `fractary/plugins` repository**

This repository is the correct baseline because:
1. It contains mature, production-tested Claude Code plugins
2. Following the Claude Code marketplace pattern, the registry lives alongside the plugin code
3. It provides real-world examples for conversion validation

## Architecture Decision: Registry Co-Location

**Key Decision from SPEC-FORGE-005 Section 3.1:**

> "The registry manifest lives in the same repository as the plugin code (e.g., `fractary/plugins/registry.json`), following the Claude Code pattern where `.claude-plugin/marketplace.json` lives with plugin code."

This means:
- ❌ **NOT** a separate `fractary/forge-registry` repository
- ✅ **YES** registry.json in this repo: `fractary/plugins/registry.json`

## What Changed from Initial Plan

### Initial Plan (FORGE-PHASE-3B)
- Create 5 FABER agent YAML files
- Place in separate `@fractary/forge/agents/` directory
- Focus on FABER-specific agents only

### Current Plan (SPEC-FORGE-005 + SPEC-FORGE-007)
- Create registry manifest system for ALL plugins
- Convert ALL mature Claude Code plugins to Fractary format
- Agents live within their respective plugins (not separate repo)
- Two-level architecture: Registry Manifest → Plugin Manifests

## Repository Structure (Target State)

```
fractary/plugins/
├── registry.json                    # ⭐ NEW: Registry manifest (root level)
│
├── plugins/                         # Existing mature plugins
│   ├── faber/                       # Core FABER plugin
│   │   ├── plugin.json              # ⭐ NEW: Plugin manifest
│   │   ├── agents/                  # ⭐ CONVERT: Agent YAML files
│   │   │   ├── frame-agent.yaml
│   │   │   ├── architect-agent.yaml
│   │   │   ├── build-agent.yaml
│   │   │   ├── evaluate-agent.yaml
│   │   │   └── release-agent.yaml
│   │   ├── tools/                   # ⭐ CONVERT: Skills → Tools YAML
│   │   ├── workflows/               # ⭐ NEW: Workflow definitions
│   │   ├── templates/               # ⭐ NEW: Template definitions
│   │   ├── commands/                # Existing (may need updates)
│   │   ├── hooks/                   # Existing (may need conversion)
│   │   └── README.md
│   │
│   ├── repo/                        # Repository management plugin
│   │   ├── plugin.json              # ⭐ NEW
│   │   ├── agents/                  # ⭐ CONVERT
│   │   ├── tools/                   # ⭐ CONVERT
│   │   └── ...
│   │
│   ├── work/                        # Work tracking plugin
│   │   ├── plugin.json              # ⭐ NEW
│   │   ├── agents/                  # ⭐ CONVERT
│   │   ├── tools/                   # ⭐ CONVERT
│   │   └── ...
│   │
│   ├── codex/                       # Memory/knowledge plugin
│   ├── file/                        # File storage plugin
│   ├── faber-cloud/                 # DevOps plugin
│   └── ... (other plugins)
│
├── specs/                           # Specifications
│   ├── SPEC-FORGE-005-REGISTRY-MANIFEST-SYSTEM.md
│   ├── SPEC-FORGE-007-CLAUDE-TO-FRACTARY-CONVERSION.md
│   └── FORGE-PHASE-3B-faber-agent-definitions.md
│
└── CLAUDE.md                        # Repository guidance
```

## Work Breakdown

### Phase 1: Infrastructure (Priority 1)
1. ✅ Create `registry.json` at repository root
2. ✅ Define registry manifest schema validation
3. ✅ Document plugin naming conventions

### Phase 2: Core Plugin Conversion (Priority 1)
Convert the foundational plugins first:

1. **faber plugin** (core FABER workflow)
   - Create `plugins/faber/plugin.json`
   - Convert 5 agents to YAML (frame, architect, build, evaluate, release)
   - Convert skills to tools (YAML format)
   - Create workflow definitions
   - Update registry.json reference

2. **work plugin** (GitHub/Jira/Linear integration)
   - Create plugin.json
   - Convert agents to YAML
   - Convert skills to tools
   - Update registry.json reference

3. **repo plugin** (source control operations)
   - Create plugin.json
   - Convert agents to YAML
   - Convert skills to tools
   - Update registry.json reference

### Phase 3: Supporting Plugins (Priority 2)
4. **file plugin** (file storage)
5. **codex plugin** (memory/knowledge)
6. **logs plugin** (logging)
7. **spec plugin** (specification management)
8. **docs plugin** (documentation)
9. **status plugin** (status line)

### Phase 4: Domain-Specific Plugins (Priority 3)
10. **faber-cloud** (AWS/Terraform)
11. **faber-app** (application development)
12. Other faber-* plugins as needed

## Conversion Process (per SPEC-FORGE-007)

For each plugin:

### 1. Create Plugin Manifest
```json
{
  "$schema": "https://fractary.com/schemas/plugin-manifest-v1.json",
  "name": "@fractary/{plugin-name}",
  "version": "2.0.0",
  "description": "...",
  "author": "Fractary Team",
  "repository": "https://github.com/fractary/plugins",
  "license": "MIT",
  "tags": ["..."],
  "agents": [...],
  "tools": [...],
  "workflows": [...],
  "templates": [...],
  "hooks": [...],
  "commands": [...],
  "config": {...}
}
```

### 2. Convert Agents
- Source: `.md` prompts or `.ts` definitions
- Target: YAML files in `agents/` directory
- Format: Fractary Agent YAML schema
- Include: system_prompt, tools, llm config, metadata

### 3. Convert Skills → Tools
- Source: TypeScript MCP tool definitions
- Target: YAML files in `tools/` directory
- Convert: Zod schemas → JSON Schema
- Document: input_schema, output_schema, implementation

### 4. Update Commands
- Source: Markdown files in `commands/`
- Target: Enhanced markdown with structured sections
- Minimal changes needed (mostly documentation improvements)

### 5. Convert Hooks
- Source: TypeScript callback functions
- Target: JavaScript files with metadata
- Convert: TS → JS, add config exports

### 6. Update Registry Manifest
Add plugin reference to `registry.json`:
```json
{
  "plugins": [
    {
      "name": "@fractary/faber-plugin",
      "version": "2.0.0",
      "description": "FABER workflow methodology",
      "manifest_url": "https://raw.githubusercontent.com/fractary/plugins/main/plugins/faber/plugin.json",
      "repository": "https://github.com/fractary/plugins",
      "license": "MIT",
      "tags": ["faber", "workflow", "official"],
      "checksum": "sha256:..."
    }
  ]
}
```

## Key Specifications to Follow

### Primary References
1. **SPEC-FORGE-005**: Registry Manifest System
   - Two-level architecture (registry → plugin manifests)
   - Directory structure and file placement
   - Manifest schemas and validation
   - Registry co-location pattern

2. **SPEC-FORGE-007**: Claude to Fractary Conversion Guide
   - Field-by-field mapping tables
   - Agent conversion patterns
   - Skill → Tool conversion (Zod → JSON Schema)
   - Command and hook conversion
   - Complete examples and checklist

### Secondary Reference
3. **FORGE-PHASE-3B**: FABER Agent Definitions
   - Detailed YAML structure for 5 FABER agents
   - System prompts and tool dependencies
   - Use as reference for agent content (but not file placement)

## Success Criteria

### Phase 1 Complete When:
- [ ] `registry.json` exists at repository root
- [ ] Registry manifest schema validation passes
- [ ] Documentation updated with new structure

### Phase 2 Complete When:
- [ ] `faber`, `work`, and `repo` plugins converted
- [ ] Each has valid `plugin.json` manifest
- [ ] Agents converted to YAML format
- [ ] Tools converted to YAML format (from skills)
- [ ] All referenced in `registry.json`
- [ ] Checksums generated and validated

### Full Conversion Complete When:
- [ ] All active plugins converted to Fractary format
- [ ] All plugin manifests validated
- [ ] Registry manifest complete and validated
- [ ] Installation tests pass: `forge install @fractary/faber-plugin`
- [ ] FABER workflow tests pass using converted plugins

## Critical Decisions Confirmed

✅ **Repository**: Work in `fractary/plugins` (this repo)
✅ **Registry Location**: `registry.json` at root (co-located with plugins)
✅ **Target Format**: Fractary YAML (canonical distribution format)
✅ **Conversion Source**: Mature Claude Code plugins in `plugins/` directory
✅ **Primary Specs**: SPEC-FORGE-005 and SPEC-FORGE-007
✅ **Architecture**: Two-level (registry manifest → plugin manifests)

## Next Steps

1. **Immediate**: Create `registry.json` skeleton
2. **Priority**: Start with FABER plugin conversion (most critical)
3. **Iterative**: Convert one plugin at a time, validate before moving to next
4. **Testing**: Test each converted plugin with `forge install` and FABER execution

## Questions Resolved

❓ Should registry be separate repo or same repo as plugins?
✅ **ANSWER**: Same repo (`fractary/plugins/registry.json`) - follows Claude Code marketplace pattern

❓ Should we use FORGE-PHASE-3B or the newer specs?
✅ **ANSWER**: Use SPEC-FORGE-005 and SPEC-FORGE-007 - they supersede PHASE-3B with registry architecture

❓ Where should agent definitions live?
✅ **ANSWER**: Within their respective plugins (e.g., `plugins/faber/agents/`), not separate `@fractary/forge/` repo

❓ Is this the right repository?
✅ **ANSWER**: Yes, `fractary/plugins` is correct baseline with mature plugins to convert

## References

- SPEC-FORGE-005: Registry Manifest System (v1.2.0)
- SPEC-FORGE-007: Claude to Fractary Conversion Guide (v1.0.0)
- FORGE-PHASE-3B: FABER Agent Definitions (for reference)
- Claude Code Marketplace: Architectural inspiration

---

**Document Status**: ✅ Confirmed and Approved
**Last Updated**: 2025-12-15
**Maintained By**: Fractary Team
