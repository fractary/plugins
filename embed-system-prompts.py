#!/usr/bin/env python3
"""
Embed system prompts from SKILL.md into tool.yaml files.
"""

import os
import sys
from pathlib import Path
import yaml

def embed_system_prompt(tool_yaml_path, skill_md_path):
    """Read tool.yaml, embed SKILL.md content as system_prompt."""

    # Read SKILL.md
    with open(skill_md_path, 'r') as f:
        skill_content = f.read()

    # Read tool.yaml
    with open(tool_yaml_path, 'r') as f:
        tool_data = yaml.safe_load(f)

    # Check if it needs updating
    if 'implementation' in tool_data and 'skill_directory' not in str(tool_data.get('implementation', {})):
        return False, "No skill_directory reference"

    # Add system_prompt
    tool_data['system_prompt'] = skill_content

    # Update implementation section
    tool_data['implementation'] = {
        'type': 'embedded',
        'scripts_directory': 'scripts'
    }

    # Write back
    with open(tool_yaml_path, 'w') as f:
        yaml.dump(tool_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return True, "Updated"

def main():
    print("=== PHASE 2: Embed System Prompts ===")
    print("")

    updated = 0
    skipped = 0
    errors = 0

    plugins = ['work', 'repo', 'file', 'codex', 'docs', 'logs', 'spec', 'status']

    for plugin in plugins:
        print(f"Processing {plugin} plugin...")

        tools_dir = Path(f'plugins/{plugin}/tools')
        if not tools_dir.exists():
            continue

        for tool_dir in tools_dir.iterdir():
            if not tool_dir.is_dir():
                continue

            tool_name = tool_dir.name
            tool_yaml = tool_dir / 'tool.yaml'
            skill_md = Path(f'plugins/{plugin}/skills/{tool_name}/SKILL.md')

            if not tool_yaml.exists():
                print(f"  ⚠️  {tool_name}: No tool.yaml (skipping)")
                continue

            if not skill_md.exists():
                print(f"  ⚠️  {tool_name}: No SKILL.md in skills/ (skipping)")
                skipped += 1
                continue

            try:
                success, message = embed_system_prompt(tool_yaml, skill_md)
                if success:
                    print(f"  ✓ Embedded system_prompt for {tool_name}")
                    updated += 1
                else:
                    print(f"  ⏭️  {tool_name}: {message} (skipped)")
                    skipped += 1
            except Exception as e:
                print(f"  ❌ {tool_name}: Error - {e}")
                errors += 1

        print("")

    print("=== SUMMARY ===")
    print(f"Tools updated: {updated}")
    print(f"Tools skipped: {skipped}")
    print(f"Errors: {errors}")

    if errors > 0:
        print("⚠️  Some tools had errors")
        return 1
    else:
        print("✅ All system prompts embedded")
        return 0

if __name__ == '__main__':
    sys.exit(main())
