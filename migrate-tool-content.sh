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
