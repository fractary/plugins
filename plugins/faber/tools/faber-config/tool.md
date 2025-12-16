---
name: faber-config
type: tool
description: 'FABER configuration management tool - loads, validates, and manages
  workflow settings

  including default workflows, autonomy levels, and domain-specific configurations.

  '
input_schema:
  type: object
  properties:
    operation:
      type: string
      enum:
      - load
      - validate
      - get_value
      - resolve_workflow
      description: Configuration operation to perform
    config_path:
      type: string
      description: Path to configuration file
      default: .fractary/plugins/faber/config.json
    key:
      type: string
      description: Configuration key to retrieve (for get_value operation)
    workflow_id:
      type: string
      description: Workflow ID to resolve (for resolve_workflow operation)
  required:
  - operation
output_schema:
  type: object
  properties:
    status:
      type: string
      enum:
      - success
      - warning
      - failure
      description: Operation status
    config:
      type: object
      description: Loaded configuration (for load operation)
    value:
      type: any
      description: Retrieved value (for get_value operation)
    workflow:
      type: object
      description: Resolved workflow definition (for resolve_workflow operation)
    validation_errors:
      type: array
      items:
        type: string
      description: Validation errors (if any)
    messages:
      type: array
      items:
        type: string
      description: Operation messages
implementation:
  type: skill-based
  skill_directory: plugins/faber/skills/faber-config
  scripts_directory: scripts
  handler: fractary-faber-plugin
  function: faber_config_operation
version: 2.0.0
author: Fractary FABER Team
tags:
- faber
- configuration
- management
- infrastructure
---

# Faber Config

Utility tool with no system prompt.
