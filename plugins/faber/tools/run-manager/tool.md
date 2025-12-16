---
name: run-manager
type: tool
description: 'FABER run management - tracks workflow runs, execution history, and
  provides

  run lifecycle operations (create, resume, list, archive).

  '
input_schema:
  type: object
  properties:
    operation:
      type: string
      enum:
      - create_run
      - get_run
      - list_runs
      - resume_run
      - archive_run
      description: Run management operation
    run_id:
      type: string
      description: Run identifier (for get/resume/archive operations)
    work_id:
      type: string
      description: Work identifier (for create_run operation)
    filters:
      type: object
      properties:
        status:
          type: string
          enum:
          - pending
          - in_progress
          - completed
          - failed
          - paused
        work_id:
          type: string
        date_range:
          type: object
          properties:
            start:
              type: string
              format: date-time
            end:
              type: string
              format: date-time
      description: Filters for list_runs operation
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
    run:
      type: object
      properties:
        run_id:
          type: string
        work_id:
          type: string
        status:
          type: string
        created_at:
          type: string
          format: date-time
        completed_at:
          type: string
          format: date-time
        phases_completed:
          type: array
          items:
            type: string
      description: Run details (for create/get/resume operations)
    runs:
      type: array
      items:
        type: object
      description: List of runs (for list_runs operation)
    messages:
      type: array
      items:
        type: string
      description: Operation messages
implementation:
  type: skill-based
  skill_directory: plugins/faber/skills/run-manager
  scripts_directory: scripts
  handler: fractary-faber-plugin
  function: run_manager_operation
version: 2.0.0
author: Fractary FABER Team
tags:
- faber
- run-management
- tracking
- history
- infrastructure
---

# Run Manager

Utility tool with no system prompt.
