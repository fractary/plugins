---
name: frame
type: tool
description: 'FABER Phase 1 - Frame skill responsible for fetching work items, classifying
  work type,

  setting up environment, and initializing workflow context. First phase in FABER
  workflow.

  '
input_schema:
  type: object
  properties:
    operation:
      type: string
      enum:
      - execute_frame
      description: Operation to perform (always "execute_frame")
    work_id:
      type: string
      description: FABER work identifier (internal tracking ID)
    source_type:
      type: string
      enum:
      - github
      - jira
      - linear
      - manual
      description: Issue tracker source system
    source_id:
      type: string
      description: External issue/ticket ID in source system
    work_domain:
      type: string
      enum:
      - engineering
      - design
      - writing
      - data
      - devops
      - research
      description: Work domain for environment setup
    autonomy:
      type: string
      enum:
      - dry-run
      - assisted
      - guarded
      - autonomous
      description: Autonomy level for execution
      default: guarded
  required:
  - operation
  - work_id
  - source_type
  - source_id
  - work_domain
output_schema:
  type: object
  properties:
    status:
      type: string
      enum:
      - success
      - warning
      - failure
      - pending_input
      description: Execution status
    work_type:
      type: string
      enum:
      - feature
      - bug
      - chore
      - patch
      description: Classified work type
    work_item:
      type: object
      properties:
        id:
          type: string
          description: Work item ID
        title:
          type: string
          description: Work item title
        description:
          type: string
          description: Work item description
        status:
          type: string
          description: Current status in tracking system
        assignee:
          type: string
          description: Assigned user
        labels:
          type: array
          items:
            type: string
          description: Labels/tags
      description: Fetched work item details
    branch_name:
      type: string
      description: Created branch name (if applicable)
    environment:
      type: object
      properties:
        ready:
          type: boolean
          description: Environment setup completed
        domain:
          type: string
          description: Configured domain
        tools_available:
          type: array
          items:
            type: string
          description: Available tools/dependencies
      description: Environment setup status
    messages:
      type: array
      items:
        type: string
      description: Execution messages and warnings
    errors:
      type: array
      items:
        type: string
      description: Error messages (if any)
implementation:
  type: skill-based
  skill_directory: plugins/faber/skills/frame
  workflow_file: workflow/basic.md
  scripts_directory: scripts
  execution_pattern: "The frame skill follows a skill-based execution pattern:\n1.\
    \ Load workflow implementation from workflow/basic.md\n2. Execute steps defined\
    \ in workflow:\n   - Fetch work item (via work-manager agent)\n   - Classify work\
    \ type\n   - Post frame start notification\n   - Setup domain-specific environment\n\
    \   - Update session state\n   - Post frame complete notification\n3. Return structured\
    \ result with work item details and environment status\n"
  handler: fractary-faber-plugin
  function: execute_frame_skill
version: 2.0.0
author: Fractary FABER Team
tags:
- faber
- workflow
- frame
- phase-1
- requirements
- classification
---

# Frame

Utility tool with no system prompt.
