# SPEC-00026: Distributed Plugin Architecture

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Created** | 2025-12-16 |
| **Author** | Claude (with human direction) |
| **Related** | SPEC-00016-sdk-architecture, SPEC-FORGE-005-registry-manifest-system |

## 1. Executive Summary

This specification defines the migration from a **centralized plugin repository** to a **distributed plugin architecture** where plugins live alongside the SDKs and services they wrap. This architectural change addresses scalability, versioning coherence, and establishes a clear third-party plugin development model.

### 1.1 Scope

This document covers:
- Migration from centralized `fractary/plugins` repository to distributed repositories
- Repository structure for domain-specific plugin hosting
- Plugin colocation patterns (plugins living with their SDKs)
- Registry system for plugin discovery and distribution
- Versioning strategy for SDK-plugin coherence
- Third-party plugin development model
- Migration path from current architecture

### 1.2 Design Goals

1. **Colocation** - Plugins live with the code they wrap for easier synchronization
2. **Version Coherence** - Plugin versions track SDK versions naturally
3. **Third-party Model** - Clear, replicable pattern for external plugin developers
4. **Ownership** - Each project owns its plugin definitions
5. **Discovery** - Central registry maintains discoverability
6. **Industry Alignment** - Follows npm/PyPI/crates.io distribution patterns

### 1.3 Key Changes

| Aspect | Current (Centralized) | Proposed (Distributed) |
|--------|----------------------|------------------------|
| **Plugin Location** | `fractary/plugins` (all plugins) | `fractary/core/plugins`, `fractary/faber/plugins`, `fractary/codex/plugins` |
| **SDK-Plugin Sync** | Cross-repo coordination | Same PR updates both |
| **Versioning** | Independent versions | Plugin version tracks SDK version |
| **Discovery** | Directory listing | Registry manifest |
| **Third-party Pattern** | Unclear | "Create plugin in your SDK repo" |

## 2. Background & Motivation

### 2.1 Current Architecture Limitations

The existing centralized `fractary/plugins` repository contains 11 plugins spanning multiple domains:

**Primitives (8):**
- work, repo, file, spec, docs, logs, status, codex

**Workflows (2):**
- faber, faber-cloud

**Meta-tooling (1):**
- faber-agent

**Problems with this approach:**

1. **Cross-repo coordination overhead**
   - SDK change in `fractary/core` requires separate PR in `fractary/plugins`
   - Version skew between SDK and plugin
   - Testing requires coordinating multiple repositories

2. **Unclear plugin ownership**
   - Who owns the `codex` plugin - the codex team or the plugins team?
   - Which repository should a contributor modify?

3. **No clear third-party model**
   - How should external developers create plugins?
   - Should they fork the centralized plugins repo?
   - How do they distribute their plugins?

4. **Versioning complexity**
   - Plugin version doesn't correspond to SDK version
   - Breaking SDK changes can silently break plugins
   - No automatic version tracking

5. **Repository sprawl**
   - Central repo grows unbounded as new plugins are added
   - Unrelated plugins share a repository
   - No clear organizational boundaries

### 2.2 Industry Patterns

Successful package ecosystems use distributed repositories with central registries:

| Ecosystem | Package Location | Discovery Mechanism |
|-----------|------------------|---------------------|
| **npm** | Distributed repos | Central registry (npmjs.com) |
| **PyPI** | Distributed repos | Central registry (pypi.org) |
| **crates.io** | Distributed repos | Central registry (crates.io) |
| **Docker Hub** | Distributed repos | Central registry (hub.docker.com) |
| **Helm Charts** | Distributed repos | Chart repositories |

**Common pattern:**
- Code lives in distributed repositories
- Registry provides discovery and metadata
- Versioning handled per package
- Clear ownership boundaries

### 2.3 Desired End State

**For Fractary developers:**
- SDK change → plugin update in same commit
- Single PR for breaking changes
- Clear ownership per domain

**For third-party developers:**
- "If you have an SDK, create a plugin in the same repo"
- Clear template to follow
- Submit registry entry to enable discovery

**For users:**
- Discover plugins via central registry
- Install from distributed repositories
- Automatic version compatibility

## 3. Proposed Architecture

### 3.1 Repository Structure

Plugins will be distributed across domain-specific repositories:

```
fractary/core                    # Primitive operations
├── packages/
│   ├── work/                    # Work tracking SDK
│   ├── repo/                    # Source control SDK
│   ├── file/                    # File storage SDK
│   ├── spec/                    # Specification SDK
│   ├── docs/                    # Documentation SDK
│   └── logs/                    # Logging SDK
└── plugins/
    ├── work/                    # Work plugin (wraps work SDK)
    ├── repo/                    # Repo plugin (wraps repo SDK)
    ├── file/                    # File plugin (wraps file SDK)
    ├── spec/                    # Spec plugin (wraps spec SDK)
    ├── docs/                    # Docs plugin (wraps docs SDK)
    ├── logs/                    # Logs plugin (wraps logs SDK)
    └── status/                  # Status display plugin

fractary/faber                   # Workflow orchestration
├── packages/
│   └── faber/                   # Faber SDK
└── plugins/
    ├── faber/                   # Core FABER plugin
    ├── faber-cloud/             # Cloud infrastructure plugin
    └── faber-agent/             # Plugin creation meta-tooling

fractary/codex                   # Knowledge management
├── mcp-server/                  # Codex MCP server
├── sdk/                         # Codex SDK (if separate)
└── plugins/
    └── codex/                   # Codex plugin

fractary/cli                     # Execution layer
├── src/
│   ├── commands/                # CLI commands
│   └── runtime/                 # Execution engine
└── config/
    └── registry.json            # Plugin registry manifest
```

### 3.2 Colocation Rationale

**Why primitives (work, repo, file, etc.) share `fractary/core`:**

These plugins are **platform-agnostic primitives** that don't belong to any specific domain:

- Not Faber-specific (can be used without FABER workflows)
- Not Codex-specific (standalone functionality)
- Shared by multiple higher-level tools
- Natural grouping as "core operations"

**Alternative considered:** Separate repos per primitive (`fractary/work`, `fractary/repo`, etc.)

**Rejected because:**
- Excessive fragmentation (8+ repositories)
- Higher maintenance overhead
- Primitives are tightly coupled (work items → repos → specs)
- All share same SDK patterns and interfaces

**Why domain plugins (faber, codex) use separate repos:**

- Domain-specific functionality
- Independent release cycles
- Different teams/ownership
- Larger scope justifies dedicated repository

### 3.3 Plugin Manifest Format

Each plugin uses **Fractary YAML format** for framework-independent distribution:

```yaml
# plugins/work/plugin.yaml
name: fractary-work
version: 1.0.0
description: Work item management across GitHub Issues, Jira, and Linear
sdk_dependency:
  package: "@fractary/core"
  version: "^1.0.0"

agents:
  - work-manager

tools:
  - issue-creator
  - issue-fetcher
  - comment-creator
  - label-manager
  - milestone-manager
  # ... (18 tools total)

configuration:
  schema: ./config/schema.json
  example: ./config/config.example.json
```

**Key fields:**
- `sdk_dependency` - Declares SDK version requirement
- `agents` - References to agent definitions
- `tools` - References to tool definitions
- `configuration` - Config schema and examples

### 3.4 Version Coherence Strategy

**Plugin versions track SDK versions:**

```json
// fractary/core/package.json
{
  "name": "@fractary/core",
  "version": "1.2.0"
}

// fractary/core/plugins/work/plugin.yaml
name: fractary-work
version: 1.2.0
sdk_dependency:
  package: "@fractary/core"
  version: "^1.2.0"
```

**Versioning rules:**

1. **Major version bump** - Breaking SDK changes require major plugin version bump
2. **Minor version bump** - New SDK features can bump plugin minor version
3. **Patch version bump** - Bug fixes use patch version
4. **Single commit** - SDK and plugin changes happen in same PR

**Example workflow:**

```bash
# Developer adds new feature to work SDK
# 1. Update SDK code
git commit -m "feat(work): add bulk issue update"

# 2. Update plugin to expose new feature
git commit -m "feat(work-plugin): add bulk-update tool"

# 3. Bump versions together
npm version minor  # Updates both @fractary/core and plugins/work/plugin.yaml

# 4. Single PR includes both changes
```

## 4. Registry System

### 4.1 Registry Manifest Structure

**Central registry** (`fractary/cli/config/registry.json`):

```json
{
  "version": "1.0.0",
  "updated": "2025-12-16T00:00:00Z",
  "plugins": [
    {
      "name": "fractary-work",
      "displayName": "Work Item Management",
      "description": "Manage issues across GitHub, Jira, and Linear",
      "repository": "https://github.com/fractary/core",
      "path": "plugins/work",
      "version": "1.0.0",
      "sdk": "@fractary/core",
      "category": "primitives",
      "tags": ["work", "issues", "jira", "linear", "github"],
      "maintainers": ["fractary-team"],
      "verified": true
    },
    {
      "name": "fractary-faber",
      "displayName": "FABER Workflow",
      "description": "Frame → Architect → Build → Evaluate → Release workflow orchestration",
      "repository": "https://github.com/fractary/faber",
      "path": "plugins/faber",
      "version": "2.1.0",
      "sdk": "@fractary/faber",
      "category": "workflows",
      "dependencies": [
        "fractary-work",
        "fractary-repo",
        "fractary-spec"
      ],
      "tags": ["workflow", "faber", "orchestration"],
      "maintainers": ["fractary-team"],
      "verified": true
    },
    {
      "name": "acme-workflows",
      "displayName": "ACME Custom Workflows",
      "description": "ACME Corp internal workflows",
      "repository": "https://github.com/acme-corp/workflows",
      "path": "plugins/workflows",
      "version": "1.0.0",
      "sdk": "@acme/workflows-sdk",
      "category": "workflows",
      "tags": ["acme", "custom"],
      "maintainers": ["acme-team"],
      "verified": false
    }
  ],
  "registries": [
    {
      "name": "fractary-official",
      "url": "https://registry.fractary.com/plugins.json",
      "verified": true,
      "priority": 1
    },
    {
      "name": "acme-corp",
      "url": "https://raw.githubusercontent.com/acme-corp/registry/main/plugins.json",
      "verified": false,
      "priority": 2
    }
  ]
}
```

### 4.2 Plugin Installation Flow

```bash
# User installs plugin
claude plugins install fractary-work

# CLI resolution process:
# 1. Read registry.json
# 2. Find fractary-work entry
# 3. Fetch from repository: https://github.com/fractary/core/plugins/work
# 4. Check SDK dependency: @fractary/core ^1.0.0
# 5. Install to: ~/.claude/plugins/marketplaces/fractary/work
```

**Installation locations:**

```
~/.claude/plugins/
└── marketplaces/
    ├── fractary/
    │   ├── work/           # From fractary/core/plugins/work
    │   ├── repo/           # From fractary/core/plugins/repo
    │   └── faber/          # From fractary/faber/plugins/faber
    └── acme-corp/
        └── workflows/       # From acme-corp/workflows/plugins/workflows
```

### 4.3 Dependency Resolution

**Plugin dependencies** are declared in `plugin.yaml`:

```yaml
# plugins/faber/plugin.yaml
name: fractary-faber
version: 2.1.0
dependencies:
  - name: fractary-work
    version: "^1.0.0"
  - name: fractary-repo
    version: "^1.0.0"
  - name: fractary-spec
    version: "^1.0.0"
```

**CLI automatically installs dependencies:**

```bash
claude plugins install fractary-faber

# Output:
# Installing fractary-faber@2.1.0...
# Resolving dependencies:
#   - fractary-work@^1.0.0 → 1.2.0
#   - fractary-repo@^1.0.0 → 1.3.0
#   - fractary-spec@^1.0.0 → 1.1.0
# Installing 4 plugins...
# ✓ fractary-work@1.2.0
# ✓ fractary-repo@1.3.0
# ✓ fractary-spec@1.1.0
# ✓ fractary-faber@2.1.0
```

### 4.4 Multiple Registry Support

**Users can add custom registries:**

```bash
# Add ACME Corp registry
claude plugins add-registry https://raw.githubusercontent.com/acme-corp/registry/main/plugins.json

# List registries
claude plugins list-registries
# Output:
# - fractary-official (verified) [priority: 1]
# - acme-corp [priority: 2]

# Remove registry
claude plugins remove-registry acme-corp
```

**Registry priority** determines resolution order when plugins exist in multiple registries.

## 5. Third-Party Plugin Model

### 5.1 Plugin Development Template

**For third-party developers wrapping their own SDK:**

```
your-company/your-sdk/
├── packages/
│   └── your-sdk/            # Your SDK code
│       ├── src/
│       └── package.json
└── plugins/
    └── your-plugin/         # Plugin wrapping your SDK
        ├── plugin.yaml      # Plugin manifest
        ├── agents/
        │   └── your-manager/
        │       └── agent.yaml
        ├── tools/
        │   ├── operation-1/
        │   │   └── tool.yaml
        │   └── operation-2/
        │       └── tool.yaml
        └── config/
            ├── schema.json
            └── config.example.json
```

**Plugin manifest example:**

```yaml
# plugins/your-plugin/plugin.yaml
name: your-company-your-plugin
version: 1.0.0
description: Your plugin description
author: Your Company
license: MIT

sdk_dependency:
  package: "@your-company/your-sdk"
  version: "^1.0.0"

agents:
  - your-manager

tools:
  - operation-1
  - operation-2

configuration:
  schema: ./config/schema.json
  example: ./config/config.example.json
```

### 5.2 Registry Submission Process

**To make your plugin discoverable:**

1. **Develop plugin** following Fractary YAML format
2. **Test locally** using Claude Code
3. **Publish to GitHub** (or other Git hosting)
4. **Submit PR to registry** adding entry to `fractary/cli/config/registry.json`

**Registry PR example:**

```json
{
  "name": "your-company-your-plugin",
  "displayName": "Your Plugin Name",
  "description": "What your plugin does",
  "repository": "https://github.com/your-company/your-sdk",
  "path": "plugins/your-plugin",
  "version": "1.0.0",
  "sdk": "@your-company/your-sdk",
  "category": "custom",
  "tags": ["your", "tags"],
  "maintainers": ["your-team"],
  "verified": false
}
```

**Verification process:**
- Fractary team reviews PR
- Checks plugin manifest validity
- Verifies installation works
- Marks `verified: true` for trusted plugins

### 5.3 Plugin Documentation

**Required documentation for third-party plugins:**

```
plugins/your-plugin/
├── README.md               # Overview, installation, usage
├── CHANGELOG.md            # Version history
├── LICENSE                 # License file
└── docs/
    ├── getting-started.md  # Quick start guide
    ├── configuration.md    # Configuration reference
    └── api.md              # Tool/agent reference
```

## 6. Migration Plan

### 6.1 Phase 1: Create Core SDK Repository

**Objective:** Establish `fractary/core` with SDK and plugins

**Tasks:**
1. Create `fractary/core` repository
2. Set up monorepo structure (packages/ and plugins/)
3. Move primitive SDK logic from `fractary/faber-sdk` to `fractary/core/packages/`
4. Move primitive plugins from `fractary/plugins` to `fractary/core/plugins/`
5. Update plugin manifests to reference `@fractary/core`
6. Set up CI/CD for monorepo
7. Publish `@fractary/core@1.0.0` to npm

**Plugins migrated:**
- work, repo, file, spec, docs, logs, status (7 plugins)

**Estimated effort:** 2-3 weeks

### 6.2 Phase 2: Move Faber Plugins

**Objective:** Consolidate FABER plugins with FABER SDK

**Tasks:**
1. Move `fractary/plugins/faber` to `fractary/faber/plugins/faber`
2. Move `fractary/plugins/faber-cloud` to `fractary/faber/plugins/faber-cloud`
3. Move `fractary/plugins/faber-agent` to `fractary/faber/plugins/faber-agent`
4. Update plugin manifests to reference `@fractary/faber`
5. Update Faber SDK to depend on `@fractary/core`
6. Publish `@fractary/faber@2.1.0` with colocated plugins

**Plugins migrated:**
- faber, faber-cloud, faber-agent (3 plugins)

**Estimated effort:** 1 week

### 6.3 Phase 3: Move Codex Plugin

**Objective:** Colocate Codex plugin with Codex SDK

**Tasks:**
1. Move `fractary/plugins/codex` to `fractary/codex/plugins/codex`
2. Update plugin manifest to reference `@fractary/codex`
3. Publish `@fractary/codex@1.0.0` with colocated plugin

**Plugins migrated:**
- codex (1 plugin)

**Estimated effort:** 3 days

### 6.4 Phase 4: Create Registry System

**Objective:** Enable discovery of distributed plugins

**Tasks:**
1. Create `fractary/cli/config/registry.json`
2. Add entries for all Fractary plugins
3. Implement registry reading in CLI
4. Update `claude plugins install` to use registry
5. Implement dependency resolution
6. Add `claude plugins add-registry` command
7. Document registry submission process

**Estimated effort:** 1-2 weeks

### 6.5 Phase 5: Archive Central Repository

**Objective:** Clean up after migration

**Tasks:**
1. Verify all plugins migrated successfully
2. Update `fractary/plugins/README.md` with migration notice
3. Add redirect notices to all moved plugins
4. Archive `fractary/plugins` repository
5. Update all documentation references

**Estimated effort:** 3 days

### 6.6 Migration Timeline

```
Week 1-3:  Phase 1 - Create fractary/core
Week 4:    Phase 2 - Move FABER plugins
Week 5:    Phase 3 - Move Codex plugin
Week 6-7:  Phase 4 - Create registry system
Week 8:    Phase 5 - Archive central repo

Total: ~8 weeks
```

## 7. Benefits & Trade-offs

### 7.1 Benefits

**Development Efficiency:**
- ✅ SDK and plugin changes in single PR
- ✅ No cross-repo coordination overhead
- ✅ Easier testing (both change together)

**Version Management:**
- ✅ Plugin version naturally tracks SDK version
- ✅ Breaking changes visible in single release
- ✅ Dependency resolution automated

**Third-Party Development:**
- ✅ Clear, replicable pattern
- ✅ "Plugin in same repo as SDK" guideline
- ✅ Registry submission well-defined

**Ownership & Boundaries:**
- ✅ Clear ownership per domain
- ✅ Logical grouping (primitives vs. workflows)
- ✅ Repository scope matches team scope

**Industry Alignment:**
- ✅ Matches npm/PyPI/Docker Hub patterns
- ✅ Familiar to external developers
- ✅ Proven scalability

### 7.2 Trade-offs

**Increased Repository Count:**
- ⚠️ More repositories to maintain
- Mitigation: Reasonable grouping (primitives share repo)

**Cross-Plugin Integration Testing:**
- ⚠️ Testing plugins together requires multi-repo setup
- Mitigation: E2E tests in CLI repository

**Discovery Complexity:**
- ⚠️ Users need registry to find plugins
- Mitigation: Central registry + CLI integration

**Migration Effort:**
- ⚠️ Non-trivial migration work (8 weeks estimated)
- Mitigation: Phased approach, backward compatibility

## 8. Open Questions & Decisions

### 8.1 Decisions Needed

**Q1: Should status plugin live in fractary/core or fractary/cli?**
- Option A: `fractary/core/plugins/status` (with other primitives)
- Option B: `fractary/cli/plugins/status` (closer to CLI)

**Recommendation:** Option A - Status is a primitive operation like others.

**Q2: Should we use monorepo or separate repos for primitives?**
- Option A: Monorepo `fractary/core` with all primitives
- Option B: Separate repos (`fractary/work`, `fractary/repo`, etc.)

**Recommendation:** Option A - Reduces fragmentation, primitives are tightly coupled.

**Q3: Where should registry.json live?**
- Option A: `fractary/cli/config/registry.json` (bundled with CLI)
- Option B: Separate `fractary/registry` repository

**Recommendation:** Option A initially, Option B if registry grows significantly.

**Q4: Should plugin dependencies be loose or strict?**
- Option A: Loose (`"^1.0.0"` - allow minor updates)
- Option B: Strict (`"1.0.0"` - exact version)

**Recommendation:** Option A - More flexible, follows npm conventions.

**Q5: How to handle plugin breaking changes?**
- Option A: Major version bump, deprecation notices
- Option B: Maintain multiple major versions simultaneously

**Recommendation:** Option A - Standard semver approach.

### 8.2 Future Considerations

**Plugin Signing/Verification:**
- GPG signatures for official plugins
- Checksum verification
- Deferred to future phase

**Marketplace UI:**
- Web interface for plugin discovery
- Search, filtering, ratings
- Deferred to future phase

**Auto-update Mechanism:**
- Automatic plugin updates
- Update notifications
- Deferred to future phase

**Plugin Testing Framework:**
- Conformance tests for third-party plugins
- Automated validation
- Deferred to future phase

## 9. Success Metrics

### 9.1 Technical Metrics

- **Version coherence:** 100% of plugins match SDK major version
- **Installation success rate:** >95% successful plugin installs
- **Dependency resolution:** <1s to resolve plugin dependencies
- **Registry freshness:** Registry updated within 24h of plugin release

### 9.2 Developer Experience Metrics

- **PR coordination:** 0 cross-repo PRs needed for SDK + plugin changes
- **Time to release:** <30min from SDK release to plugin release
- **Third-party adoption:** >3 verified third-party plugins within 6 months

### 9.3 User Experience Metrics

- **Discovery time:** <2min to find relevant plugin via registry
- **Installation time:** <30s to install plugin with dependencies
- **Update frequency:** Monthly plugin updates without breaking changes

## 10. References

### 10.1 Related Specifications

- [SPEC-00016: SDK Architecture](./SPEC-00016-sdk-architecture.md) - Overall SDK architecture
- [SPEC-FORGE-005: Registry Manifest System](./SPEC-FORGE-005-REGISTRY-MANIFEST-SYSTEM.md) - Registry implementation details
- [SPEC-FORGE-007: Claude to Fractary Conversion](./SPEC-FORGE-007-CLAUDE-TO-FRACTARY-CONVERSION.md) - Format conversion

### 10.2 External References

- [npm Registry Architecture](https://docs.npmjs.com/cli/v10/using-npm/registry)
- [PyPI Simple Repository API](https://packaging.python.org/specifications/simple-repository-api/)
- [Cargo Registry Protocol](https://doc.rust-lang.org/cargo/reference/registry-index.html)
- [Helm Chart Repositories](https://helm.sh/docs/topics/chart_repository/)

### 10.3 Repository Links

- Current: [fractary/plugins](https://github.com/fractary/plugins)
- Proposed: [fractary/core](https://github.com/fractary/core) (to be created)
- Proposed: [fractary/faber](https://github.com/fractary/faber) (existing)
- Proposed: [fractary/codex](https://github.com/fractary/codex) (existing)
- Proposed: [fractary/cli](https://github.com/fractary/cli) (existing)

## Appendix A: Example Migration Commit Sequence

### A.1 Migrating Work Plugin to fractary/core

```bash
# In fractary/core repository

# Commit 1: Add work SDK
git commit -m "feat(work): add work tracking SDK with GitHub/Jira/Linear support"

# Commit 2: Add work plugin
git commit -m "feat(work-plugin): add work plugin wrapping work SDK"

# Commit 3: Version bump
npm version minor  # Bumps both SDK and plugin to 1.1.0

# Commit 4: Update registry
# (Separate PR to fractary/cli)
git commit -m "chore(registry): add fractary-work plugin"
```

### A.2 SDK Breaking Change Workflow

```bash
# In fractary/core repository

# Commit 1: Breaking SDK change
git commit -m "feat(work)!: rename getIssue to getWorkItem"

# Commit 2: Update plugin to match
git commit -m "feat(work-plugin)!: update for renamed SDK methods"

# Commit 3: Major version bump
npm version major  # Bumps both SDK and plugin to 2.0.0

# Commit 4: Update changelog
git commit -m "docs: add breaking change notes to CHANGELOG.md"
```

## Appendix B: Plugin Manifest Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "version", "description"],
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "description": "Plugin identifier (kebab-case)"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version (semver)"
    },
    "description": {
      "type": "string",
      "description": "Brief description of plugin functionality"
    },
    "author": {
      "type": "string",
      "description": "Plugin author or organization"
    },
    "license": {
      "type": "string",
      "description": "SPDX license identifier"
    },
    "sdk_dependency": {
      "type": "object",
      "required": ["package", "version"],
      "properties": {
        "package": {
          "type": "string",
          "description": "npm package name of SDK"
        },
        "version": {
          "type": "string",
          "description": "Semver range for SDK version"
        }
      }
    },
    "dependencies": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "version"],
        "properties": {
          "name": {
            "type": "string",
            "description": "Dependent plugin name"
          },
          "version": {
            "type": "string",
            "description": "Semver range for plugin version"
          }
        }
      }
    },
    "agents": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of agent identifiers"
    },
    "tools": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of tool identifiers"
    },
    "configuration": {
      "type": "object",
      "properties": {
        "schema": {
          "type": "string",
          "description": "Path to configuration JSON schema"
        },
        "example": {
          "type": "string",
          "description": "Path to example configuration file"
        }
      }
    }
  }
}
```

## Appendix C: Registry Manifest Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "plugins"],
  "properties": {
    "version": {
      "type": "string",
      "description": "Registry format version"
    },
    "updated": {
      "type": "string",
      "format": "date-time",
      "description": "Last update timestamp (ISO 8601)"
    },
    "plugins": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "repository", "path", "version"],
        "properties": {
          "name": {"type": "string"},
          "displayName": {"type": "string"},
          "description": {"type": "string"},
          "repository": {"type": "string", "format": "uri"},
          "path": {"type": "string"},
          "version": {"type": "string"},
          "sdk": {"type": "string"},
          "category": {
            "type": "string",
            "enum": ["primitives", "workflows", "custom"]
          },
          "dependencies": {
            "type": "array",
            "items": {"type": "string"}
          },
          "tags": {
            "type": "array",
            "items": {"type": "string"}
          },
          "maintainers": {
            "type": "array",
            "items": {"type": "string"}
          },
          "verified": {"type": "boolean"}
        }
      }
    },
    "registries": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "url"],
        "properties": {
          "name": {"type": "string"},
          "url": {"type": "string", "format": "uri"},
          "verified": {"type": "boolean"},
          "priority": {"type": "integer", "minimum": 1}
        }
      }
    }
  }
}
```
