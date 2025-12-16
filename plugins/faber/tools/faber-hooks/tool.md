---
name: faber-hooks
type: tool
description: 'FABER hooks system - manages phase-level callbacks for custom behavior,

  enabling extensibility and integration points in workflows.

  '
input_schema:
  type: object
  properties:
    operation:
      type: string
      enum:
      - execute_hook
      - list_hooks
      - register_hook
      description: Hook operation to perform
    hook_type:
      type: string
      enum:
      - pre_phase
      - post_phase
      - pre_step
      - post_step
      - on_error
      - on_complete
      description: Type of hook to execute
    phase:
      type: string
      description: Phase context for hook
    context:
      type: object
      description: Hook execution context
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
    hook_results:
      type: array
      items:
        type: object
      description: Results from executed hooks
    messages:
      type: array
      items:
        type: string
      description: Hook execution messages
implementation:
  type: skill-based
  skill_directory: plugins/faber/skills/faber-hooks
  scripts_directory: scripts
  handler: fractary-faber-plugin
  function: faber_hooks_operation
version: 2.0.0
author: Fractary FABER Team
tags:
- faber
- hooks
- callbacks
- extensibility
- infrastructure
---

# Faber Hooks

Utility tool with no system prompt.
