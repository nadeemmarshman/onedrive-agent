# AI Agent Build — Handoff Brief

**Purpose of this document:** This is a context handoff for a project in progress, written so Claude (in a new chat, with no prior memory) can pick up exactly where things left off. Upload this as a Project knowledge file.

---

## Who I am / context

{{owner}} — hybrid Business Analyst / IT Project Manager based in Johannesburg, South Africa. Targeting both BA and PM roles. Currently unemployed and job hunting. Background includes {{employerA}} (BA-focused), NCR Atleos/{{employerB}} (PM-focused), Agile delivery, payments systems, stakeholder management. Holds a Diploma in Business Analysis and Project Management, PSM I certification. No PMP/PRINCE2.

This Project ("Career Portfolio & Job Search") holds career portfolio work generally — resume drafting, job search tracking, and technical portfolio projects. This document covers one specific build within that Project.

---

## The project: build a small, portfolio-grade AI agent

**Origin of the idea:** Started from a practical task (cleaning up duplicate/bloated files in OneDrive) but was deliberately reframed as a *learning + portfolio* exercise rather than just getting the cleanup done. The OneDrive cleanup is the live example/use case the agent operates on — not the end goal in itself.

### Why this project, specifically

I'm a BA/PM with strong Agile and stakeholder skills, but no hands-on technical build artifact. Many BA/PM candidates can talk about AI conceptually; few can point to something they actually built. This project is meant to:

1. **Differentiate on my resume** — e.g. a bullet like: *"Designed and built a tool-calling AI agent (Python + Anthropic API) automating file deduplication and format optimization, including a human-in-the-loop approval gate for destructive actions."*
2. **Serve as a portfolio artifact** — something to show in an interview, walk through live, or link to (GitHub repo with a clean README).
3. **Demonstrate BA/PM discipline applied to a technical build** — framed as requirements → design → build → safety/governance, not just "I learned to code."

### What I'll personally walk away with

- A working (if small) agent that organizes a real folder
- A clear mental model of the agent loop: **tool-definition → decision → action → observation**
- Reusable knowledge for evaluating any agent product (Claude Code, MCP connectors, Cowork, etc.) since they all run on this same loop at larger scale

---

## The core concept (agent loop)

An "agent" is fundamentally:

1. **Tools** — discrete functions with a defined input/output contract (e.g. `list_files(folder)`, `get_file_hash(path)`, `delete_file(path)`)
2. **Decision (the LLM)** — given a goal and current state, the model decides which tool to call and with what arguments
3. **Action** — the tool actually executes
4. **Observation** — the result feeds back to the model
5. Repeat until the goal is done

Every agent product (Claude Code, Claude in Chrome, MCP connectors) is this same loop with different tools plugged in. This build makes that loop small, visible, and hand-built so I understand it directly rather than just using a finished product.

---

## The 6-phase plan

| Phase | What we build | Portfolio angle / README section |
|---|---|---|
| 0 | Confirm GitHub + Python + API key | Setup (not shown in portfolio) |
| 1 | Define tools as plain Python functions (no AI yet) — e.g. `scan_folder()`, `find_duplicates()`, `find_convertible_files()`, `propose_action()` | "Requirements & functional design" |
| 2 | Wrap each function with a JSON-schema tool contract (name, description, parameters) — same format used by MCP and the Anthropic API | "Technical design / tool contracts" |
| 3 | Build the decision loop manually via the Anthropic API (a script, not claude.ai) — send goal + tool definitions + folder state, Claude responds with a structured tool call | Core build — the actual agent |
| 4 | Execute the chosen tool, feed result back, let Claude decide the next step, loop 3–4 iterations on a real/sample OneDrive folder | Demo / walkthrough section (maybe screen recording) |
| 5 | Add a human-approval gate before any destructive action (e.g. deletion) executes | "Risk & governance" — the BA/PM differentiator |
| 6 | Polish: clean documented code, README (problem → approach → architecture → outcome), Git/GitHub repo, optional architecture diagram, draft resume bullet | The actual shareable/linkable deliverable |
| 7 | Compare the hand-built agent to Claude Cowork (Anthropic's own production agent) — try Cowork (e.g. a free trial of Pro, if available) on a similar file-organizing task and note where it matches/exceeds the hand-built version, and why | "Evaluating other agent products" section in README — demonstrates I can assess production agent tooling, not just build a toy one |

**Note on Phase 7:** Cowork is essentially Anthropic's own polished version of the exact tool-definition → decision → action loop built by hand in Phases 3-4. Comparing the two — after, not before, building my own — is the point: it shows I understand the mechanics well enough to evaluate a finished product critically, rather than just using it. Requires a paid plan (Pro/Max/Team/Enterprise) and macOS or Windows; not available on the free tier. Do this last, once Phases 1-6 are complete.

**Status: Phase 0 in progress.**
- Python: ✅ confirmed installed — Python 3.14.5, 64-bit, Windows
- GitHub account: ❓ unconfirmed — need to check via github.com password reset using likely personal email, or create new if none exists
- Anthropic API key: ❓ not yet created — needs console.anthropic.com signup, Settings → API Keys → Create Key (separate billing from claude.ai subscription; free tier credit covers this project many times over)

---

## Decisions already made (don't re-litigate these)

- **Framing:** Hybrid BA/PM positioning, not BA-only or PM-only.
- **Why not just clean the OneDrive folder directly:** A connector-based approach (Microsoft 365 MCP connector) was tried first and failed — the connector requires a work/school Microsoft account, and I only have a personal Microsoft account, so that route is closed.
- **Why not just use Claude in Chrome or a one-off script:** Considered, but rejected as the *primary* path because the goal is to learn agent architecture, not just get OneDrive tidied — those options either don't teach the tool-calling loop (script) or don't let me configure/see the underlying mechanics (Claude in Chrome is a finished product, good for observing agent behavior but not for building it).
- **Repo will be portfolio-grade from the start** — not a throwaway script. Clean code, documented, version-controlled, README written the way a hiring manager/recruiter would read it.

---

## How to resume

Next concrete step: finish Phase 0 (confirm/create GitHub account, create Anthropic API key), then start Phase 1 — defining the plain Python tool functions for OneDrive scanning, duplicate detection, and format-conversion candidates.

When resuming, Claude should:
- Treat this as already-agreed scope — don't re-ask whether I want to do this or re-explain what an agent is from scratch.
- Pick up at the phase marked "in progress" above, or wherever I indicate we left off.
- Keep README/resume framing hybrid BA/PM throughout.

## Standing rule: keep this document current (free tier — no cross-conversation memory)

I'm on the free Claude tier. Project knowledge files like this one are visible across every chat in the Project, but the free tier doesn't carry the cross-conversation memory that paid accounts get — so this document is doing the job memory would otherwise do. If it goes stale, future chats will resume from outdated assumptions.

**At the start of every new phase (or whenever a significant decision is made — e.g. a changed tool stack, a finished phase, a new blocker), Claude should proactively offer to regenerate this handoff document** with the updated status, decisions, and next step, rather than waiting to be asked. I'll then re-upload the refreshed version to replace this one in the Project knowledge.
