# V0.5-Joker (v0.5.0)

**Programmable Execution Firewall, 28-Command Binary Impulse Rule Engine, and Multi-Connector Policy Runtime**

`V0.5-Joker` is a 100% offline execution firewall and adaptive policy runtime compiled into a single `672.5 KB` (`windows-x64`) pure `std` Safe Rust binary (`#![forbid(unsafe_code)]`) with zero external dependencies, zero Docker, and zero cloud calls. It ships with **`100` parallel execution units enabled by default** (`--teams 1..=100` hard cap), compiles human-authored `.rules` policies into fixed **16-byte binary impulses**, and secures AI coding agents, `n8n` workflows, and local HTTP/CLI pipelines simultaneously across 4 transport-only connectors.

> **Note on Repository Contents:** This public repository contains the official documentation, `presets/`, `SHA256SUMS.txt`, and `LICENSE`. Compiled cross-platform binaries (`windows-x64`, `linux-x64`, `macos-arm64`, `macos-x64`) are distributed exclusively through the official release package below.

---

## Get V0.5-Joker ($29 One-Time License)

**[Get V0.5-Joker ($29 One-Time License) on Polar.sh](https://buy.polar.sh/polar_cl_QNGodSf74F49VETHe1vvIYGvsiEDsqTuNax5V0i8ck1)**

What is included in your license package:
- Pre-compiled standalone binaries for **Windows x64 (`joker.exe`)**, **Linux x64 (`joker`)**, **macOS ARM64 (`joker`)**, and **macOS x64 (`joker`)**
- **`SHA256SUMS.txt`** checksum manifest for every binary and archive
- All **6 production presets** (`ai-agent.rules`, `api-guard.rules`, `n8n.rules`, `strict-sandbox.rules`, `joker.mcp.json`, `joker-hook.py`)
- Complete documentation and `100` parallel execution units unlocked out of the box

---

## Core Architecture & Guarantees

1. **Two-Layer Policy Enforcement (`L1` Deterministic + `L2` Adaptive)**
   - **Layer 1 (`L1` Baseline):** Enforces hard execution boundaries against path traversal (`..`), NUL-byte smuggling, symlink/junction escapes, and destructive system commands (`rm -rf`, `del /f`, `format`, `shutdown`) alongside immutable `L1` rules (`DENY`, `LOCK`, `STOP`, `REDACT`). Learned weights or `L2` approvals can never override an `L1` block, whereas an explicit `L1 ALLOW` overrides a conflicting `L2 DENY`.
   - **Layer 2 (`L2` Adaptive Policy):** Supports dynamic runtime approvals/rejections (`approve`, `reject`), live rule edits, shard routing, and adaptive pathway weights updated continuously from real execution outcomes.
2. **16-Byte Binary Impulse Compilation (`FNV-1a` + Edge-Aware Wildcards)**
   - Textual `.rules` directives never enter internal evaluation state as raw strings. Each rule compiles into a fixed **16-byte little-endian C-ABI impulse**:
     - `0..8` (`u64` LE): `target_hash` (64-bit `FNV-1a` of normalized key)
     - `8..12` (`i32` LE): `value` (threshold, seconds, quota bytes, shard ID, or weight delta)
     - `12` (`u8`): `op_code` (`1..=28`; `0` emitted as neutral impulse when no rule matches)
     - `13` (`u8`): `flags` bitmask (`0x01` = `L1`, `0x02` = `L2`, `0x04` = `*` global wildcard, `0x08` = `prefix*` edge-aware token/string prefix, `0x10` = `*sub*` / `*suffix` contains match)
     - `14..16` (`[u8; 2]`): zero alignment padding
3. **Child Isolation (`.env_clear()`), Built-In DLP, & Cryptographic Persistence**
   - Spawned processes and proxied MCP servers run with `.env_clear()`, preserving only safe baseline OS variables (`PATH`, `SYSTEMROOT`, `COMSPEC`, `TEMP`, `TMP`, `HOME`, `USERPROFILE`, `LANG`).
   - Built-in secret patterns (`sk-proj-`, `sk_live_`, `sk_test_`, `sk-`, `ghp_`, `github_pat_`, `AKIA`, `AIza`, plus `--api-key` / `LAK_API_KEY`) and custom `REDACT` rules scrub secrets to `[REDACTED]`.
   - Every action is recorded in an append-only FIPS 180-4 SHA-256 hash chain (`audit.log`) and persisted via atomic checkpoints (`kernel.snap`, `CRC32` + `FNV-1a` verified).

---

## Step-by-Step Installation & Usage Guide

### 1. Platform Setup & Checksum Verification

After downloading the release package, verify archive integrity against `SHA256SUMS.txt`:

- **Windows (`windows-x64`):**
  ```powershell
  (Get-FileHash .\Joker-v0.5.0-windows-x64.zip -Algorithm SHA256).Hash
  Expand-Archive .\Joker-v0.5.0-windows-x64.zip -DestinationPath .\joker
  .\joker\joker.exe --data-dir .lak-data --cmd "status"
  ```
- **Linux (`linux-x64`):**
  ```bash
  sha256sum -c SHA256SUMS.txt --ignore-missing
  unzip Joker-v0.5.0-linux-x64.zip -d ./joker
  chmod +x ./joker/joker
  ./joker/joker --data-dir .lak-data --cmd "status"
  ```
- **macOS (`macos-arm64` / `macos-x64`):**
  ```bash
  shasum -a 256 Joker-v0.5.0-macos-*.zip
  unzip Joker-v0.5.0-macos-arm64.zip -d ./joker
  chmod +x ./joker/joker
  ./joker/joker --data-dir .lak-data --cmd "status"
  ```

### 2. One-Click IDE Integration (`--setup` & `--wrap-existing`)

Automatically discover IDE MCP configs (Cursor, Claude Desktop, Windsurf, Antigravity), create `.bak` backups, and register Joker idempotently:

```bash
# Standalone Joker MCP setup with a .rules preset
./joker --setup --rules presets/ai-agent.rules --data-dir .lak-data

# Wrap all existing third-party MCP servers through Joker --mcp-proxy
./joker --setup --wrap-existing --rules presets/ai-agent.rules --data-dir .lak-data
```

### 3. The 4 Transport-Only Connectors

#### Connector A: MCP (`--mcp-stdio` & `--mcp-proxy`)
- **Direct MCP Server (`--mcp-stdio`):** Exposes 5 tools over JSON-RPC 2.0:
  1. `joker_eval` (`target`, optional `dry_run`): Compiles/evaluates `target` against active rules and returns `EVAL_OK` / `EVAL_BLOCKED` (or `DRY_RUN_OK` / `DRY_RUN_BLOCKED`).
  2. `joker_rules` (`action`: `list|add|del|mod|reload`, optional `rule`, `selector`, `index`): Manages active rules dynamically at runtime.
  3. `joker_pulse` (`payload`, optional `channel`): Sends an explicit sensory pulse (`team=<id>` supported) through the runtime.
  4. `kernel_status`: Reports shard counts, active weights, policy block totals, checksums, and `audit_head`.
  5. `kernel_audit_verify`: Validates the entire FIPS 180-4 SHA-256 `audit.log` hash chain.
- **Universal MCP Proxy (`--mcp-proxy`):** Intercepts any downstream MCP server (`--target <bin>` or `-- <cmd> <args...>`), validates tool names and nested JSON arguments, enforces `BREAK` thresholds, scrubs secrets, and normalizes disguised `401`/`403`/`token expired` errors into `isError: true`:
  ```bash
  ./joker --data-dir .lak-data --rules presets/ai-agent.rules \
    --mcp-proxy -- npx -y @modelcontextprotocol/server-filesystem .
  ```

#### Connector B: Native Hook (`--hook`)
Built directly into the binary for zero-overhead `PreToolUse` and `PostToolUse` interception:
```bash
./joker --data-dir .lak-data --rules presets/ai-agent.rules --hook < hook_payload.json
```
- **`PreToolUse`:** Evaluates `tool_input.command`, `file_path`, `path`, or `url`; exits with **code `2`** and writes the redacted reason to `stderr` on block.
- **`PostToolUse`:** Checks `tool_response` for `isError: true`, rule `STOP`/deny hits, `401 unauthorized`, `403 forbidden`, `"error_class": "forbidden"`, `token expired`, `authentication failed`, or `inhibitor_circuit_breaker`, and emits `{"continue":false,"stopReason":"Joker Hook Hard-Stop (...)"}`.

#### Connector C: CLI (`--cli` & `--cmd`)
Run an interactive REPL (`--cli`) or inline one-shot commands (`--cmd`):
```bash
./joker --data-dir .lak-data --rules presets/ai-agent.rules \
  --cmd "rule list" \
  --cmd "eval cargo test --release" \
  --cmd "audit"
```
Supported CLI commands: `help`, `status`, `eval <target>`, `dry-run <target>`, `rule <list|add|del|mod|reload>`, `pulse [channel] <payload>`, `step [count]`, `approve [pattern]`, `reject [pattern]`, `freeze [rel_path]`, `reset`, `audit`, `exit`.

#### Connector D: Local HTTP API (`--serve <addr>` for `n8n` & Webhooks)
Hardened HTTP/1.1 & JSON-RPC server (`Content-Length <= 65,536` bytes, constant-time token check via `LAK_API_KEY` env var or `--api-key <token>` with `X-API-Key` or `Authorization: Bearer`):
```bash
export LAK_API_KEY="replace_with_strong_local_secret"
./joker --data-dir .lak-data --rules presets/n8n.rules --serve 127.0.0.1:8090
```
- `POST /eval`: `{"target": "webhook_payment_ok", "dry_run": false}` (returns `200 OK` when allowed, `403 Forbidden` when blocked in live mode, or `200 OK` with `DRY_RUN_BLOCKED` when `dry_run: true`).
- `GET /rules` & `POST /rules`: List rules (`GET`) or mutate live (`POST` with `{"action": "add|del|mod|reload|list", ...}`).
- `POST /pulse`, `POST /approve`, `POST /reject`, `GET /status`, `GET /audit`, `POST /exit`.

### 4. Dry-Run Simulation (`--dry-run`) & Live Monitor (`--monitor`)

```bash
# Evaluate policies in memory with zero disk mutation (disk_modified=false)
./joker --rules presets/strict-sandbox.rules --dry-run --cmd "eval powershell -Command whoami"

# Live terminal monitor or single-frame snapshot
./joker --monitor --rules presets/ai-agent.rules --data-dir .lak-data
./joker --monitor --once --rules presets/ai-agent.rules --data-dir .lak-data
```

---

## Complete 28-Command Rule Language Reference

Rules follow the syntax `[L1 | L2] <COMMAND> [target_or_quoted_pattern] [integer_value]` with `#` or `//` comments. Rules without a layer prefix default to **`L1`**. Numeric-threshold commands (`BREAK`, `TIMEOUT`, `RATE_LIMIT`, `RETRY`, `QUOTA`, `REWARD`, `PENALIZE`, `PRUNE`, `ALERT`) support single-integer shorthand (for example `L1 BREAK 3`, which sets `target="*"` and `value=3`).

### 7 Core Commands (`Opcode 1` to `7`)

| Opcode & Keyword | Category | Default / Typical Layer | Arguments & Default Value | Exact Runtime Behavior | Example |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **`1` · `ALLOW`** | Core | Default `L1` (`L1` or `L2`) | `<target>` `[val=1]` | Permits matching command, binary, or payload (`verdict=ALLOW`). In `L2`, registers an approved dynamic policy; in `L1`, overrides any conflicting `L2 DENY` (`ALLOW_L1_OVERRIDE`). | `L2 ALLOW cargo 1` |
| **`2` · `DENY`** | Core | Default `L1` (`L1` or `L2`) | `<target>` `[val=1]` | Blocks matching command, path, or token (`DENY_L1` with `hard_stop=true`, or `DENY_L2` synced to persistent Layer 2 reject rules). | `L1 DENY "rm -rf" 1` |
| **`3` · `REDACT`** | Core | Default `L1` (`L1`) | `<pattern>` `[val=1]` | Scrubs matching tokens (exact, `prefix*`, or `*sub*`) to `[REDACTED]` across evaluated inputs, MCP outputs, proxy responses, and hook snippets (`REDACT *` safely no-ops). | `L1 REDACT sk-* 1` |
| **`4` · `STOP`** | Core | Default `L1` (`L1`) | `<pattern>` `[val=1]` | Highest-priority halt (`allowed=false`, `hard_stop=true`, `verdict=STOP`). Forces `isError: true` with `hard_stop: true` in `--mcp-proxy` and `{"continue": false}` in `--hook`. | `L1 STOP 401_UNAUTHORIZED 1` |
| **`5` · `BREAK`** | Core | Default `L1` (`L1`) | `<strikes>` or `<target> <strikes>` `[default=3]` | Sets the consecutive-failure threshold (`break_threshold`) that trips `INHIBITOR_CIRCUIT_BREAKER` on repeated failing calls. | `L1 BREAK 3` |
| **`6` · `PREFER`** | Core | Default `L1` (`L2`) | `<target>` `[delta=10]` | Adds positive `preferred_delta` (`max(1, val)`) when `<target>` matches, reinforcing adaptive pathway weights during evaluation. | `L2 PREFER cargo 20` |
| **`7` · `ROUTE`** | Core | Default `L1` (`L2`) | `<target>` `[shard_id=0]` | Routes matching evaluations deterministically to shard `shard_id % team_count` (`routed_team`), isolating learned pathway weights per workload. | `L2 ROUTE webhook 1` |

### 21 Pro Controls (`Opcode 8` to `28`)

| Opcode & Keyword | Category | Default / Typical Layer | Arguments & Default Value | Exact Runtime Behavior | Example |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **`8` · `TIMEOUT`** | Pro | Default `L1` (`L1`) | `<secs>` or `<target> <secs>` `[default=30]` | Sets active execution timeout (`timeout_secs`) in evaluation metadata and runtime policy state. | `L1 TIMEOUT 30` |
| **`9` · `RATE_LIMIT`** | Pro | Default `L1` (`L1`) | `<rpm>` or `<target> <rpm>` `[default=120]` | Sets `rate_limit` ceiling on matching evaluations and emits opcode `9` impulse with `value=<rpm>`. | `L1 RATE_LIMIT 60` |
| **`10` · `RETRY`** | Pro | Default `L1` (`L1`) | `<count>` or `<target> <count>` `[default=2]` | Encodes bounded retry budget (`value=<count>`, opcode `10`) into the 16-byte impulse stream. | `L1 RETRY 2` |
| **`11` · `QUOTA`** | Pro | Default `L1` (`L1`) | `<bytes>` or `<target> <bytes>` `[default=65536]` | Encodes payload/resource byte ceiling (`value=<bytes>`, opcode `11`) into the impulse stream. | `L1 QUOTA 32768` |
| **`12` · `ENV_CLEAR`** | Pro | Default `L1` (`L1`) | `[target=*]` `[val=1]` | Declares strict child environment clearing in the compiled rule set alongside `.env_clear()` process isolation. | `L1 ENV_CLEAR * 1` |
| **`13` · `ENV_ALLOW`** | Pro | Default `L1` (`L1`) | `<VAR_NAME>` `[val=1]` | Declares an explicitly permitted environment variable (`<VAR_NAME>`) in the policy manifest via opcode `13`. | `L1 ENV_ALLOW PATH 1` |
| **`14` · `SANDBOX`** | Pro | Default `L1` (`L1`) | `[target=*]` `[val=1]` | Marks workspace confinement enforcement in the compiled policy baseline and emits opcode `14` impulse. | `L1 SANDBOX * 1` |
| **`15` · `LOCK`** | Pro | Default `L1` (`L1`) | `<path_or_pattern>` `[val=1]` | Hard-locks a path or resource pattern: blocks identically to `DENY` (`DENY_L1` with `hard_stop=true` on `L1`, or `DENY_L2` on `L2`) with `LOCK <pattern>` reason. | `L1 LOCK C:\Windows\* 1` |
| **`16` · `REWARD`** | Pro | Default `L1` (`L1` or `L2`) | `<delta>` or `<target> <delta>` `[default=10]` | Reinforces matching safe actions by adding `+max(1, delta)` to `preferred_delta`, raising adaptive pathway weights. | `L1 REWARD safe_probe 10` |
| **`17` · `PENALIZE`** | Pro | Default `L1` (`L1` or `L2`) | `<delta>` or `<target> <delta>` `[default=-10]` | Penalizes matching risky actions by subtracting `abs(delta)` from `preferred_delta` without hard-blocking. | `L1 PENALIZE unsafe_action -20` |
| **`18` · `FALLBACK`** | Pro | Default `L1` (`L2`) | `<route_name>` `[val=1]` | Registers a named fallback target (`<route_name>`) and emits opcode `18` impulse (`FNV-1a` hashed on `<route_name>`). | `L2 FALLBACK retry_queue 1` |
| **`19` · `PRUNE`** | Pro | Default `L1` (`L1`) | `<top_k>` or `<target> <top_k>` `[default=6]` | Compiles tool/context pruning budget (`value=<top_k>`, opcode `19`) into the policy impulse stream. | `L1 PRUNE 6` |
| **`20` · `AUDIT`** | Pro | Default `L1` (`L1`) | `[target=*]` `[val=1]` | Sets `audit_required=true` in evaluation metadata and emits opcode `20` impulse alongside SHA-256 `audit.log` recording. | `L1 AUDIT * 1` |
| **`21` · `CHECKPOINT`** | Pro | Default `L1` (`L1` or `L2`) | `[target=*]` `[val=1]` | Emits opcode `21` checkpoint impulse for matching state transitions alongside atomic `kernel.snap` persistence. | `L2 CHECKPOINT * 1` |
| **`22` · `ROLLBACK`** | Pro | Default `L1` (`L1`) | `[target=*]` `[val=1]` | Emits opcode `22` rollback directive impulse on matching targets within zero-trust profiles. | `L1 ROLLBACK * 1` |
| **`23` · `VERIFY`** | Pro | Default `L1` (`L1`) | `[target=*]` `[val=1]` | Emits opcode `23` integrity-verification impulse on matching API/payload evaluations. | `L1 VERIFY * 1` |
| **`24` · `RESET`** | Pro | Default `L1` (`L1`) | `[target=*]` `[val=1]` | Emits opcode `24` state-reset directive impulse when matching patterns fire (pair with CLI `reset` for clean reinitialization). | `L1 RESET * 1` |
| **`25` · `ATTACH`** | Pro | Default `L1` (`L1`) | `<scope_name>` `[val=1]` | Binds a named scope tag (`<scope_name>`) via opcode `25` impulse (`FNV-1a` hash of `<scope_name>`). | `L1 ATTACH sandbox 1` |
| **`26` · `WATCH`** | Pro | Default `L1` (`L1`) | `<scope_name>` `[val=1]` | Marks `<scope_name>` for active observation, emitting opcode `26` impulse on matching inputs. | `L1 WATCH sandbox 1` |
| **`27` · `ALERT`** | Pro | Default `L1` (`L1`) | `<level>` or `<target> <level>` `[default=1]` | Sets `alert_triggered=true` in evaluation metadata and emits opcode `27` impulse. | `L1 ALERT * 1` |
| **`28` · `LOG`** | Pro | Default `L1` (`L2`) | `[target=*]` `[val=1]` | Emits opcode `28` telemetry logging impulse for matching workflow events without altering allow/deny verdicts. | `L2 LOG * 1` |

### Live Runtime Rule CRUD (`list`, `add`, `mod`, `del`, `reload`)

- **CLI:** `rule list`, `rule add L2 DENY curl 1`, `rule mod 0 L1 DENY "curl -k" 1`, `rule del idx=0` (or `rule del curl`), `rule reload`.
- **MCP (`joker_rules`):** `{"action": "add", "rule": "LOCK vault_keys.json"}`, `{"action": "mod", "index": 22, "rule": "ALLOW vault_keys.json"}`, `{"action": "del", "selector": "vault_keys.json"}`, `{"action": "reload"}`.
- **HTTP (`GET /rules` & `POST /rules`):**
  ```bash
  curl -s http://127.0.0.1:8090/rules -H "X-API-Key: $LAK_API_KEY"
  curl -s -X POST http://127.0.0.1:8090/rules -H "X-API-Key: $LAK_API_KEY" \
    -H "Content-Type: application/json" -d '{"action":"add","rule":"L2 DENY wget 1"}'
  ```

---

## Included Presets (`presets/`)

| Preset File | Target Environment | Summary |
| :--- | :--- | :--- |
| `presets/ai-agent.rules` | AI Coding Assistants | `SANDBOX`, `ENV_CLEAR`, `DENY` system dirs & `"rm -rf"`/`"del /f"`, `REDACT` (`sk-*`, `ghp_*`, `AKIA*`), `STOP 401_UNAUTHORIZED`, `BREAK 3`, `TIMEOUT 30`, `PRUNE 6`, `L2 ALLOW/PREFER/ROUTE` for `cargo`, `git`, `python`. |
| `presets/api-guard.rules` | External API Gateways | `ENV_CLEAR`, `REDACT` (`sk-*`, `sk_live_*`, `ghp_*`, `AKIA*`, `AIza*`), `STOP` (`401`, `403`, `"token expired"`, `"authentication failed"`), `RATE_LIMIT 60`, `QUOTA 32768`, `BREAK 3`, `VERIFY`, `ALERT`, `AUDIT`. |
| `presets/n8n.rules` | `n8n` & Webhooks | `ENV_CLEAR`, `RATE_LIMIT 120`, `QUOTA 65536`, `TIMEOUT 20`, `RETRY 2`, `BREAK 3`, `REDACT` (`sk-*`, `ghp_*`, `Bearer_*`), `DENY "rm -rf"`, `STOP` (`401_UNAUTHORIZED`, `403_FORBIDDEN`), `L2 ALLOW/ROUTE/PREFER webhook`, `FALLBACK retry_queue`, `LOG`. |
| `presets/strict-sandbox.rules` | Zero-Trust Lockdown | `SANDBOX`, `LOCK` (`/etc/*`, `C:\Windows\*`, `C:\Users\*`), `DENY` (`powershell`, `cmd`, `bash`, `sh`, `curl`, `wget`), `REDACT`, `BREAK 2`, `TIMEOUT 15`, `REWARD`/`PENALIZE`, `ROLLBACK`, `RESET`, `ATTACH`/`WATCH sandbox`. |
| `presets/joker.mcp.json` | MCP Client Config | Ready-to-use `--mcp-stdio` entry loading `presets/ai-agent.rules` and `.lak-data`. |
| `presets/joker-hook.py` | Claude Code Hook | Thin `stdin` JSON forwarder invoking `--rules presets/ai-agent.rules --hook`. |

---

## Verified Live Benchmarks & Stress Tests

All metrics below are from real execution runs on `V0.5-Joker (v0.5.0)`:

- **Release Test Suite:** `62/62` tests passing (`61` library + `1` CLI default/cap test).
- **Default 100-Unit Boot & Hard Cap Enforcement:**
  ```text
  STATUS ... teams=100 total_cells=700 ... active_nodes=7 tick=0 ... audit_entries=1
  joker.exe --teams 500 --cmd "status" -> FATAL_TIER_ERROR: --teams must be within 1..=100 (got 500)
  ```
- **500-Request HTTP `/eval` Stress Benchmark (`n8n.rules` + SHA-256 Disk Append):**
  - `500 HTTP /eval calls: ok=250, blocked=250 | Total=5163.1 ms | Avg=10.33 ms/req`
  - Post-stress `--monitor --once`: `Audit Log: 3041 entries | SHA-256 Chain: VERIFIED_OK | Tick: 1000 | Active 16B Impulses=22 | Layer1 Blocks=502 | Layer2 Blocks=0 | Redactions=0`
- **Native Hook (`--hook`):**
  - `PreToolUse` (`rm -rf /`): `exit=2` (blocked before execution)
  - `PostToolUse` (`isError: true`, `401 Unauthorized`): `{"continue":false,"stopReason":"Joker Hook Hard-Stop (PASS): {\"isError\":true,\"content\":[{\"type\":\"text\",\"text\":\"401 Unauthorized\"}]}"}`
- **Live IDE MCP Verification (`--mcp-stdio`):**
  - `--dry-run` on `C:\Windows\win.ini`: `DRY_RUN_BLOCKED verdict=BLOCK_L1 ... disk_modified=false` (`tick=0` and `audit_entries=19` unchanged).
  - Live CRUD lifecycle: `joker_rules add "LOCK vault_keys.json"` (`RULE_ADD_OK idx=22 op=15 size=16`) -> `eval` (`EVAL_BLOCKED verdict=BLOCK_L1`) -> `mod 22 "ALLOW vault_keys.json"` (`RULE_MOD_OK`) -> `eval` (`EVAL_OK verdict=ALLOW`) -> `del vault_keys.json` (`RULE_DEL_OK removed=1`) -> `eval` (`EVAL_OK verdict=PASS`).
  - Secret scrubbing: `joker_eval` on `TOKEN=ghp_liveSecretToken99887766` returned `EVAL_OK ... redactions=1 target="TOKEN=[REDACTED]"`.
  - Final audit check: `AUDIT_VERIFIED_OK entries=38 head_hash=c4fa805cdd0528bc4b3ce90158faf7abb6c396b01bdcd4db91c50a8870c28d12`.

---

## License

See [LICENSE](./LICENSE) for full licensing terms.
