#!/usr/bin/env python3
"""
Convert Fractary YAML definitions to Markdown format.

This script converts:
- tool.yaml → tool.md (with frontmatter + body)
- agent.yaml → agent.md (with frontmatter + body)

Following the new Fractary standard:
https://github.com/fractary/forge/blob/main/docs/definitions/README.md
"""

import os
import sys
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

def parse_embedded_skill_md(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse SKILL.md content that was embedded in tool.yaml.
    Separates frontmatter from body content.

    Returns:
        (frontmatter_dict, body_content)
    """
    # Check if content starts with frontmatter (---)
    if not content.strip().startswith('---'):
        # No frontmatter, return empty dict and full content
        return {}, content.strip()

    # Split by --- to extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        # Malformed frontmatter
        return {}, content.strip()

    frontmatter_yaml = parts[1].strip()
    body = parts[2].strip()

    try:
        frontmatter = yaml.safe_load(frontmatter_yaml) or {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, body


def convert_tool_yaml_to_md(tool_yaml_path: Path) -> Tuple[bool, str]:
    """
    Convert tool.yaml to tool.md format.

    Extracts:
    1. Frontmatter from tool.yaml
    2. Embedded SKILL.md content from system_prompt field
    3. Parses SKILL.md frontmatter and body
    4. Creates tool.md with combined frontmatter + body content

    Returns:
        (success, message)
    """
    tool_dir = tool_yaml_path.parent
    tool_name = tool_dir.name
    tool_md_path = tool_dir / 'tool.md'

    # Read tool.yaml
    try:
        with open(tool_yaml_path, 'r') as f:
            tool_data = yaml.safe_load(f)
    except Exception as e:
        return False, f"Failed to read YAML: {e}"

    # Extract system_prompt (which contains embedded SKILL.md)
    system_prompt = tool_data.get('system_prompt', '')

    if not system_prompt:
        # Some tools might not have system_prompt (utility tools)
        # Just convert the YAML to MD format
        frontmatter = {k: v for k, v in tool_data.items() if k != 'system_prompt'}
        body = f"# {tool_data.get('name', tool_name).replace('-', ' ').title()}\n\nUtility tool with no system prompt."
    else:
        # Parse embedded SKILL.md to separate its frontmatter from body
        skill_frontmatter, skill_body = parse_embedded_skill_md(system_prompt)

        # Build new frontmatter for tool.md
        frontmatter = {
            'name': tool_data.get('name', tool_name),
            'type': 'tool',
            'description': tool_data.get('description', skill_frontmatter.get('description', '')),
            'version': tool_data.get('version', '1.0.0'),
        }

        # Add tags if present
        if 'tags' in tool_data:
            frontmatter['tags'] = tool_data['tags']
        elif 'tags' in skill_frontmatter:
            frontmatter['tags'] = skill_frontmatter['tags']

        # Add parameters if present
        if 'input_schema' in tool_data:
            frontmatter['parameters'] = tool_data['input_schema']

        # Add implementation if present
        if 'implementation' in tool_data:
            impl = tool_data['implementation']
            # Clean up implementation (remove deprecated fields)
            if impl.get('type') == 'embedded':
                impl['type'] = 'bash'  # Convert embedded to bash type
            frontmatter['implementation'] = impl

        # Preserve model preference from SKILL.md if present
        if 'model' in skill_frontmatter:
            if 'llm' not in frontmatter:
                frontmatter['llm'] = {}
            frontmatter['llm']['model'] = skill_frontmatter['model']

        # Body is the actual skill content (below SKILL.md frontmatter)
        body = skill_body if skill_body else f"# {tool_name.replace('-', ' ').title()}\n\n(No content)"

    # Write tool.md
    try:
        with open(tool_md_path, 'w') as f:
            f.write('---\n')
            yaml.dump(frontmatter, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            f.write('---\n\n')
            f.write(body)
            f.write('\n')

        return True, f"Converted to {tool_md_path.name}"
    except Exception as e:
        return False, f"Failed to write MD: {e}"


def convert_agent_yaml_to_md(agent_yaml_path: Path) -> Tuple[bool, str]:
    """
    Convert agent.yaml to agent.md format.

    Moves system_prompt to body, keeps other fields in frontmatter.

    Returns:
        (success, message)
    """
    agent_dir = agent_yaml_path.parent
    agent_name = agent_dir.name
    agent_md_path = agent_dir / 'agent.md'

    # Read agent.yaml
    try:
        with open(agent_yaml_path, 'r') as f:
            agent_data = yaml.safe_load(f)
    except Exception as e:
        return False, f"Failed to read YAML: {e}"

    # Extract system_prompt
    system_prompt = agent_data.pop('system_prompt', '')

    # Build frontmatter (everything except system_prompt)
    frontmatter = agent_data.copy()

    # Ensure required fields
    if 'type' not in frontmatter:
        frontmatter['type'] = 'agent'
    if 'version' not in frontmatter:
        frontmatter['version'] = '1.0.0'

    # Body is the system_prompt content
    body = system_prompt if system_prompt else f"# {agent_name.replace('-', ' ').title()}\n\n(No content)"

    # Write agent.md
    try:
        with open(agent_md_path, 'w') as f:
            f.write('---\n')
            yaml.dump(frontmatter, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            f.write('---\n\n')
            f.write(body)
            f.write('\n')

        return True, f"Converted to {agent_md_path.name}"
    except Exception as e:
        return False, f"Failed to write MD: {e}"


def main():
    print("=== Converting YAML to Markdown Format ===")
    print()

    plugins_dir = Path('plugins')

    converted_tools = 0
    converted_agents = 0
    skipped = 0
    errors = 0

    # Convert tools
    print("Converting tools...")
    for tool_yaml in plugins_dir.glob('*/tools/*/tool.yaml'):
        plugin_name = tool_yaml.parts[1]
        tool_name = tool_yaml.parent.name

        success, message = convert_tool_yaml_to_md(tool_yaml)
        if success:
            print(f"  ✓ {plugin_name}/{tool_name}: {message}")
            converted_tools += 1
        else:
            print(f"  ❌ {plugin_name}/{tool_name}: {message}")
            errors += 1

    print()

    # Convert agents
    print("Converting agents...")
    for agent_yaml in plugins_dir.glob('*/agents/*/agent.yaml'):
        plugin_name = agent_yaml.parts[1]
        agent_name = agent_yaml.parent.name

        success, message = convert_agent_yaml_to_md(agent_yaml)
        if success:
            print(f"  ✓ {plugin_name}/{agent_name}: {message}")
            converted_agents += 1
        else:
            print(f"  ❌ {plugin_name}/{agent_name}: {message}")
            errors += 1

    print()
    print("=== SUMMARY ===")
    print(f"Tools converted: {converted_tools}")
    print(f"Agents converted: {converted_agents}")
    print(f"Errors: {errors}")
    print()

    if errors > 0:
        print("⚠️  Some conversions had errors")
        return 1
    else:
        print("✅ All conversions completed successfully")
        return 0


if __name__ == '__main__':
    sys.exit(main())
