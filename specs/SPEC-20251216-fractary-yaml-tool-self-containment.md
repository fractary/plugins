---
title: "Make Fractary YAML Tools Self-Contained"
slug: fractary-yaml-tool-self-containment
created: 2025-12-16
refined: 2025-12-16
status: draft
type: refactoring
priority: critical
affected_plugins:
  - work
  - repo
  - file
  - codex
  - docs
  - logs
  - spec
  - status
total_tools_affected: 84
changelog:
  - date: 2025-12-16
    type: refinement
    changes:
      - "Clarified: Embed system_prompt in tool.yaml (not reference external file)"
      - "Clarified: Skip copying scripts if they already exist in tool directory"
      - "Clarified: Keep skills/ directories for now, cleanup in separate PR"
      - "Added: Pre-migration inventory showing existing scripts"
      - "Updated Phase 2 script to embed SKILL.md content"
---

# SPEC: Make Fractary YAML Tools Self-Contained

## 1. Executive Summary

During the Claude Code to Fractary YAML conversion, **84 tool definitions across 8 plugins** were created as sparse stubs that reference external `skills/` directories. This violates the Fractary architecture principle that tools should be self-contained entities.

**Problem:** Tools reference external skills directories
**Solution:** Make each tool self-contained with all content in its own directory
**Effort:** Medium - Automated migration with validation (~30 minutes)
**Risk:** Low - Copy operation with validation, can be rolled back

## 2. Problem Statement

### 2.1 Current Architecture (Incorrect)

```
plugins/work/
├── tools/
│   └── issue-creator/
│       └── tool.yaml          # Sparse stub pointing to skills/
└── skills/
    └── issue-creator/
        ├── SKILL.md            # System prompt
        └── scripts/            # Scripts (optional)
```

**tool.yaml content:**
```yaml
name: issue-creator
type: tool
description: Create new issues

implementation:
  type: skill-based
  skill_directory: plugins/repo/skills/issue-creator  # WRONG! External reference
  source_file: SKILL.md
```

### 2.2 Target Architecture (Correct)

```
plugins/work/
├── tools/
│   └── issue-creator/
│       ├── tool.yaml           # Complete definition
│       ├── SKILL.md            # System prompt (local)
│       └── scripts/            # Scripts (local, if needed)
└── skills/                     # TO BE REMOVED or archived
```

**tool.yaml content (Embed system prompt):**
```yaml
name: issue-creator
type: tool
description: Create new issues

system_prompt: |
  # Issue Creator Tool

  <CONTEXT>
  You are the issue-creator tool...
  [Full SKILL.md content embedded here]
  </CONTEXT>

  <WORKFLOW>
  ...
  </WORKFLOW>

implementation:
  type: script-based
  scripts_directory: scripts
```

**Decision**: Embed the full system_prompt in tool.yaml rather than referencing external files. This ensures:
- Complete self-containment (no file references)
- Single source of truth for tool behavior
- Easier to validate and audit
- No dependency on external markdown files

### 2.3 Why This Matters

1. **Self-Containment**: Each tool should be a complete, independent entity
2. **Portability**: Tools can be moved/shared without breaking references
3. **Clarity**: Everything needed for a tool is in one place
4. **Architecture**: Aligns with Fractary's design principles
5. **No External Dependencies**: No cross-references between tools/ and skills/

## 3. Impact Assessment

| Plugin | Tools | Has Scripts | Complexity |
|--------|-------|-------------|------------|
| work   | 18    | Some        | Medium     |
| repo   | 15    | Most        | Medium     |
| file   | 8     | Some        | Medium     |
| codex  | 13    | Some        | Medium     |
| docs   | 8     | Few         | Low        |
| logs   | 13    | Few         | Low        |
| spec   | 7     | Few         | Low        |
| status | 2     | Few         | Low        |
| **TOTAL** | **84** | **~40%** | **Medium** |

### 3.1 What Needs Migration

For each of 84 tools:
- ✅ SKILL.md exists in skills/ directory
- ⚠️ Scripts may or may not exist
- ✅ tool.yaml exists but is sparse
- ❌ No content currently in tools/ directory except tool.yaml

### 3.2 Current State Analysis

```bash
# Tools have minimal content (some already have scripts/)
$ ls plugins/work/tools/issue-creator/
tool.yaml

$ ls plugins/work/tools/handler-work-tracker-github/
scripts/
tool.yaml

# Skills have the actual content
$ ls plugins/work/skills/issue-creator/
SKILL.md
```

### 3.3 Pre-Migration Inventory

**Tools that already have scripts/ directories:**
- work: 6 tools
- repo: 8 tools
- file: ~3 tools
- codex: ~5 tools

**Action**: Skip copying scripts if they already exist in tools/ directory.

## 4. Remediation Plan

### Phase 1: Copy Supporting Files (Automated)

**Objective:** Copy scripts, workflow, and other supporting files from skills/ to tools/ directories (skip if exists)

**Note:** SKILL.md will be embedded into tool.yaml in Phase 2, not copied as a separate file.

**Script:**
```bash
#!/bin/bash
# migrate-tool-content.sh

echo "=== PHASE 1: Copy Supporting Files ==="
echo ""

copied=0
skipped=0

for plugin in work repo file codex docs logs spec status; do
  echo "Processing $plugin plugin..."

  for tool_dir in plugins/$plugin/tools/*/; do
    tool_name=$(basename "$tool_dir")
    skill_dir="plugins/$plugin/skills/$tool_name"

    if [ ! -d "$skill_dir" ]; then
      echo "  ⚠️  No skill directory for $tool_name (skipping)"
      continue
    fi

    # Copy scripts directory if it exists in skills/ but NOT in tools/
    if [ -d "$skill_dir/scripts" ] && [ ! -d "$tool_dir/scripts" ]; then
      cp -r "$skill_dir/scripts" "$tool_dir/"
      echo "  ✓ Copied scripts/ for $tool_name"
      ((copied++))
    elif [ -d "$tool_dir/scripts" ]; then
      echo "  ⏭️  scripts/ already exists for $tool_name (skipped)"
      ((skipped++))
    fi

    # Copy workflow directory if it exists in skills/ but NOT in tools/
    if [ -d "$skill_dir/workflow" ] && [ ! -d "$tool_dir/workflow" ]; then
      cp -r "$skill_dir/workflow" "$tool_dir/"
      echo "  ✓ Copied workflow/ for $tool_name"
      ((copied++))
    elif [ -d "$tool_dir/workflow" ]; then
      echo "  ⏭️  workflow/ already exists for $tool_name (skipped)"
      ((skipped++))
    fi
  done
  echo ""
done

echo "=== SUMMARY ==="
echo "Directories copied: $copied"
echo "Directories skipped (already exist): $skipped"
echo "✅ Phase 1 complete"
```

**Files affected:** Scripts/workflow directories that don't already exist
**Risk:** Low - copy operation with skip-if-exists
**Duration:** ~1 minute

### Phase 2: Embed System Prompts in tool.yaml (Automated)

**Objective:** Read SKILL.md from skills/, embed content as system_prompt in tool.yaml, remove skill_directory references

**Script:**
```bash
#!/bin/bash
# embed-system-prompts.sh

echo "=== PHASE 2: Embed System Prompts ==="
echo ""

updated=0
errors=0

for plugin in work repo file codex docs logs spec status; do
  echo "Processing $plugin plugin..."

  for tool_yaml in plugins/$plugin/tools/*/tool.yaml; do
    tool_dir=$(dirname "$tool_yaml")
    tool_name=$(basename "$tool_dir")
    skill_dir="plugins/$plugin/skills/$tool_name"
    skill_md="$skill_dir/SKILL.md"

    # Check if SKILL.md exists in skills directory
    if [ ! -f "$skill_md" ]; then
      echo "  ⚠️  $tool_name: No SKILL.md in skills/ (skipping)"
      continue
    fi

    # Check if tool.yaml has skill_directory reference (needs update)
    if grep -q "skill_directory:" "$tool_yaml"; then
      # Create backup
      cp "$tool_yaml" "$tool_yaml.bak"

      # Remove the implementation section with skill_directory
      sed -i '/^implementation:/,/^[a-z]/{ /^implementation:/d; /^  /d; }' "$tool_yaml"
      # Clean up any trailing implementation lines
      sed -i '/^implementation:/,$ { /skill_directory/d; /source_file/d; /scripts_directory/d; /workflow_directory/d; }' "$tool_yaml"

      # Read SKILL.md content and indent for YAML
      skill_content=$(cat "$skill_md" | sed 's/^/  /')

      # Append system_prompt with embedded content
      cat >> "$tool_yaml" <<EOF

system_prompt: |
$skill_content

implementation:
  type: embedded
  scripts_directory: scripts
EOF

      # Remove backup if successful
      rm "$tool_yaml.bak"

      echo "  ✓ Embedded system_prompt for $tool_name"
      ((updated++))
    else
      echo "  ⏭️  $tool_name: No skill_directory reference (skipping)"
    fi
  done
  echo ""
done

echo "=== SUMMARY ==="
echo "Tools updated: $updated"
echo "Errors: $errors"

if [ $errors -gt 0 ]; then
  echo "⚠️  Some tools had errors"
  exit 1
else
  echo "✅ All system prompts embedded"
fi
```

**Files affected:** 84 tool.yaml files
**Risk:** Medium - modifies YAML structure, backups created
**Duration:** ~3 minutes

### Phase 3: Validation (Automated)

**Objective:** Verify all tools have embedded system_prompt and no external references

**Script:**
```bash
#!/bin/bash
# validate-tool-self-containment.sh

echo "=== PHASE 3: Validation ==="
echo ""

errors=0
warnings=0
success=0

for plugin in work repo file codex docs logs spec status; do
  for tool_yaml in plugins/$plugin/tools/*/tool.yaml; do
    tool_dir=$(dirname "$tool_yaml")
    tool_name=$(basename "$tool_dir")

    # Check that tool.yaml HAS system_prompt embedded
    if ! grep -q "^system_prompt:" "$tool_yaml"; then
      echo "❌ $plugin/$tool_name: Missing embedded system_prompt"
      ((errors++))
      continue
    fi

    # Check that tool.yaml DOESN'T reference skills/
    if grep -q "skill_directory:" "$tool_yaml"; then
      echo "❌ $plugin/$tool_name: Still has skill_directory reference"
      ((errors++))
      continue
    fi

    # Check if scripts are referenced but missing (warning only)
    if grep -q "scripts_directory:" "$tool_yaml"; then
      if [ ! -d "$tool_dir/scripts" ]; then
        echo "⚠️  $plugin/$tool_name: References scripts but directory missing"
        ((warnings++))
      fi
    fi

    ((success++))
  done
done

echo ""
echo "=== SUMMARY ==="
echo "Success: $success tools self-contained"
echo "Errors: $errors"
echo "Warnings: $warnings"

if [ $errors -eq 0 ]; then
  echo "✅ All tools are self-contained"
else
  echo "❌ Validation failed - $errors errors found"
  exit 1
fi
```

**Expected result:** Zero errors, 84 tools self-contained
**Risk:** None - validation only
**Duration:** ~1 minute

### Phase 4: Cleanup (Deferred)

**Objective:** Archive or remove the old skills/ directories

**Decision:** Keep skills/ directories for now. Cleanup will be done in a separate PR after verifying the migration is successful.

**Future cleanup options:**
1. **Archive** - Move to `plugins/{plugin}/.archive/skills/`
2. **Remove** - Delete entirely (once confirmed working)

**This phase is OUT OF SCOPE for this PR.**

## 5. Rollback Plan

If issues arise after migration:

```bash
# Restore from git (Phase 1-2 only)
git checkout -- plugins/*/tools/*/tool.yaml
git clean -fd plugins/*/tools/*/

# Restore from archive (Phase 4 only)
for plugin in work repo file codex docs logs spec status; do
  if [ -d "plugins/$plugin/.archive/skills" ]; then
    mv "plugins/$plugin/.archive/skills" "plugins/$plugin/"
  fi
done
```

## 6. Success Criteria

- [ ] All 84 tool.yaml files have embedded system_prompt
- [ ] All tool.yaml files have NO skill_directory reference
- [ ] Scripts/workflow copied to tool directories where missing
- [ ] Validation passes with zero errors
- [ ] At least one tool from each plugin executes successfully

## 7. Timeline

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Copy Supporting Files | 1 min | Pending |
| 2 | Embed System Prompts | 3 min | Pending |
| 3 | Validation | 1 min | Pending |
| 4 | Cleanup | - | Deferred to separate PR |
| **Total** | | **5 min** | |

## 8. Dependencies

- Git access for rollback
- Write access to plugins/ directory
- Shell (bash) for automation scripts

## 9. Notes

### Architecture Decision

**Why remove skill_directory reference?**
- Fractary tools should be self-contained entities
- External references create fragile dependencies
- Portability - tools should work independently
- Clarity - everything in one place

### Future Migration Path

This sets up for the planned migration to Markdown-based format where:
- System prompt will be the main markdown content
- Metadata will be in YAML frontmatter
- Tools remain self-contained

### Relationship to FABER Plugin

The FABER plugin uses a similar but different pattern:
- FABER has complex multi-file workflows
- FABER tools coordinate multiple skills
- This is appropriate for orchestration
- Regular tools should be simpler and self-contained

## 10. Appendix: Tool Inventory

### Work Plugin (18 tools)
cli-helper, comment-creator, comment-lister, handler-work-tracker-github,
handler-work-tracker-jira, handler-work-tracker-linear, issue-assigner,
issue-classifier, issue-creator, issue-fetcher, issue-linker, issue-searcher,
issue-updater, label-manager, milestone-manager, state-manager, work-common,
work-initializer

### Repo Plugin (15 tools)
branch-manager, branch-namer, branch-puller, branch-pusher, cleanup-manager,
commit-creator, config-wizard, handler-source-control-bitbucket,
handler-source-control-github, handler-source-control-gitlab, permission-manager,
pr-manager, repo-common, tag-manager, worktree-manager

### File Plugin (8 tools)
common, config-wizard, file-manager, handler-storage-gcs, handler-storage-gdrive,
handler-storage-local, handler-storage-r2, handler-storage-s3

### Codex Plugin (13 tools)
cache-clear, cache-health, cache-list, cache-metrics, cli-helper, config-helper,
config-migrator, document-fetcher, handler-http, handler-sync-github, org-syncer,
project-syncer, repo-discoverer

### Docs Plugin (8 tools)
doc-auditor, doc-classifier, doc-consistency-checker, doc-lister, doc-validator,
doc-writer, docs-director-skill, docs-manager-skill

### Logs Plugin (13 tools)
log-analyzer, log-archiver, log-auditor, log-capturer, log-classifier,
log-director-skill, log-lister, log-manager-skill, log-searcher, log-summarizer,
log-validator, log-writer

### Spec Plugin (7 tools)
spec-archiver, spec-generator, spec-initializer, spec-linker, spec-lister,
spec-validator, work-linker

### Status Plugin (2 tools)
status-aggregator, status-formatter
