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

    # Check that tool.yaml DOESN'T reference skills/ anymore
    if grep -q "skill_directory:" "$tool_yaml"; then
      echo "❌ $plugin/$tool_name: Still has skill_directory reference"
      ((errors++))
      continue
    fi

    # For tools with embedded type, check system_prompt exists
    if grep -q "type: embedded" "$tool_yaml"; then
      if ! grep -q "^system_prompt:" "$tool_yaml"; then
        echo "❌ $plugin/$tool_name: Has embedded type but missing system_prompt"
        ((errors++))
        continue
      fi
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
