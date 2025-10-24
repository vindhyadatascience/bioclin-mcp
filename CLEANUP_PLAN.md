# Authentication & Documentation Consolidation Plan

## Executive Summary

The project has accumulated **21 authentication-related files** with significant redundancy and confusion. This plan consolidates them into a clean, maintainable structure.

## Current Problems

### 1. Redundant Scripts (DELETE 2, KEEP 1)
- ✅ **KEEP**: `docker-login.sh` (root) - Most complete, handles env vars + prompts
- ❌ **DELETE**: `scripts/docker-login.sh` - Legacy X11 version, rarely used
- ❌ **MERGE INTO ROOT**: `scripts/docker-cli-login.sh` - Functionality in main script

### 2. Duplicate Python Auth Code (DELETE 1, KEEP 1)
- ✅ **KEEP**: `src/bioclin_auth.py` - Complete, supports all methods
- ❌ **DELETE**: `src/auto_browser_auth.py` - Redundant, functionality in main file

### 3. Overlapping Docker Documentation (CONSOLIDATE 5 → 2)
- ✅ **KEEP & ENHANCE**: `docs/DOCKER_AUTH.md` - Primary Docker auth reference
- ✅ **KEEP**: `QUICKSTART_DOCKER.md` - Quick reference card
- ❌ **MERGE**: `DOCKER_ONLY_SETUP.md` → Move unique content to DOCKER_AUTH.md
- ❌ **MERGE**: `docs/DOCKER.md` → Move deployment content to main README
- ❌ **DELETE**: `scripts/manual-login-guide.md` - Outdated manual cookie method

### 4. Legacy/Outdated Files (DELETE 3)
- ❌ **DELETE**: `scripts/run_bioclin.sh` - Hardcoded miniconda path, use uv/docker
- ❌ **DELETE**: `config/example_config.json` - Outdated, superseded by README
- ❌ **DELETE**: `.env` - Local file with credentials (already in .gitignore)

### 5. Config Files (CONSOLIDATE 2 → 1)
- ✅ **KEEP & ENHANCE**: `config/claude-desktop-config.json` - Add all 3 methods
- ❌ **DELETE**: Redundant example configs

## Proposed New Structure

```
bioclin-mcp/
├── README.md                          # Main doc with all install methods
├── QUICKSTART_DOCKER.md               # Docker quick ref
├── QUICKSTART_UV.md                   # uv quick ref
│
├── docs/
│   ├── AUTHENTICATION.md              # Browser/CLI auth guide
│   └── DOCKER_AUTH.md                 # Docker-specific auth
│
├── src/
│   └── bioclin_auth.py                # Single auth implementation
│
├── scripts/
│   └── build.sh                       # Docker build helper
│
├── config/
│   └── claude-desktop-config.json     # All 3 methods: Docker, uv, pip
│
└── docker-login.sh                    # Root-level auth helper
```

## Files to DELETE (9 files)

1. `src/auto_browser_auth.py` - Redundant auth code
2. `scripts/docker-login.sh` - Legacy X11 version
3. `scripts/docker-cli-login.sh` - Merged into root docker-login.sh
4. `scripts/run_bioclin.sh` - Outdated launcher
5. `scripts/manual-login-guide.md` - Outdated manual method
6. `DOCKER_ONLY_SETUP.md` - Content merged to DOCKER_AUTH.md
7. `docs/DOCKER.md` - Deployment content moved to README
8. `config/example_config.json` - Outdated
9. `.env` - Remove from repo (already in .gitignore)

## Files to UPDATE (5 files)

### 1. `README.md`
- ✅ Already has: Docker, uv, pip installation methods
- Add: Link to all quickstarts at top
- Add: Deployment section from docs/DOCKER.md
- Clarify: Authentication flow for each method

### 2. `docs/DOCKER_AUTH.md`
- Add: Content from DOCKER_ONLY_SETUP.md
- Add: Troubleshooting from docs/DOCKER.md
- Keep: Environment variable documentation
- Streamline: Remove redundant examples

### 3. `docs/AUTHENTICATION.md`
- Remove: References to auto_browser_auth.py
- Update: All examples use bioclin_auth.py
- Add: Clear "Prerequisites" section
- Simplify: Architecture diagrams

### 4. `docker-login.sh`
- Add: Comment explaining it replaces scripts/docker-*.sh
- Keep: Current implementation (already best version)

### 5. `config/claude-desktop-config.json`
- Expand to show all 3 methods:
  ```json
  {
    "mcpServers": {
      "bioclin-docker": { ... },
      "bioclin-uv": { ... },
      "bioclin-pip": { ... }
    }
  }
  ```

## Migration Checklist

- [ ] Create `.env.example` template (no credentials)
- [ ] Remove `.env` from working directory
- [ ] Delete 9 redundant files
- [ ] Update 5 files with consolidated content
- [ ] Update all internal documentation links
- [ ] Test all 3 installation methods still work
- [ ] Update CHANGELOG
- [ ] Commit with detailed message

## Expected Benefits

1. **Clarity**: Single source of truth for each topic
2. **Maintainability**: Less duplication = easier updates
3. **User Experience**: Clear path for each use case
4. **Security**: Remove credential files
5. **Reduced Confusion**: No more "which script do I use?"

## Validation Criteria

After cleanup, users should:
- ✅ Find exactly ONE way to authenticate for their use case
- ✅ Have clear quickstart for their chosen method (Docker/uv/pip)
- ✅ Not encounter broken links in documentation
- ✅ Be able to set up in <5 minutes with any method
