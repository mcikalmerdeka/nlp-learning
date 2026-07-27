# Context Management

## The Context Problem

AI agents have limited context windows. Every token counts. Wasted context = degraded reasoning = worse output. Managing context is a core competency of a world-class agent.

---

## Context Budget Principles

### The 50% Rule
When context reaches ~50% of the window, proactively compact. Don't wait until you're forced to.

### Every Token Must Earn Its Place
Before including anything in context, ask:
- Does this directly help solve the current task?
- Can I summarize this instead of including it verbatim?
- Is this already known from the conversation history?
- Would a file reference suffice instead of the full content?

### Read Before Claiming, But Don't Read Everything
- Read files that are directly relevant to the current task
- Use search tools (grep, ast-grep) to find specific patterns without reading entire files
- Batch read multiple files when you know they're all needed
- Stop reading once you have sufficient understanding

---

## Context Compaction Strategy

### When to Compact
- Context exceeds 50% of window
- Starting a new sub-task within the same session
- Switching from exploration to implementation
- Before making a complex, multi-step change

### How to Compact
1. **Summarize conversation history** — Replace long exchanges with key decisions and current state
2. **Remove completed work** — Move done items to a summary; keep only what's still open
3. **Replace file contents with references** — "See `src/auth.ts` for implementation" vs. full file content
4. **Use todo lists** — Track state externally (todo tool) instead of in conversation
5. **Extract key findings** — Move exploration results into a concise summary

### The Compact Format
```
## Session Summary
- Task: [one-line description]
- Status: [in progress / blocked / completed]
- Key decisions: [bullet list]
- Open items: [from todo list]
- Relevant files: [file paths only, not contents]
```

---

## Session Discipline

### One Task Per Session
Switching tasks mid-session degrades quality. Use `/clear` or start a new session when pivoting.

### Session Lifecycle
1. **Setup** — Load relevant skills, read initial files, clarify requirements
2. **Exploration** — Search codebase, understand patterns, identify files to change
3. **Implementation** — Make changes, verify, test
4. **Verification** — Run tests, check for regressions, confirm requirements met
5. **Handoff** — Summarize what changed, what's still open, what needs follow-up

### Handoff Documentation
When ending a session or passing to another agent:
- What was completed
- What is still in progress
- What decisions were made and why
- What blockers exist
- What files were changed
- What tests were run and their results

---

## Parallel Execution & Context

### When to Parallelize
- Multiple independent file reads
- Multiple search queries
- Multiple test runs
- Independent implementation tasks

### When NOT to Parallelize
- Tasks that depend on each other's output
- Tasks that modify the same files
- Tasks that share mutable state

### Context Isolation
Each parallel agent/worker should receive:
- The specific task it's responsible for
- The minimal context needed for that task
- Clear boundaries on what it should NOT touch

---

## Codebase Navigation Without Context Bloat

### Grepping > Reading
Use grep/ast-grep to find specific patterns without loading entire files into context.

### Symbol Search > File Reading
Use LSP symbol search to find where something is defined, then read only that definition.

### References > Full Content
When you've already read a file once, reference it by path. Don't re-read it unless you need to verify current state.

### Tree > List
Use `tree` with depth limits to understand structure without listing every file.

---

## Memory Management for Long Sessions

### Progressive Disclosure
1. Start with high-level overview (tree, key files)
2. Read relevant files as needed
3. Compact and summarize before diving deeper
4. Reference, don't repeat

### The Rule of Three
If you find yourself re-reading the same file more than 3 times in a session, something is wrong:
- You didn't understand it the first time (take notes)
- You're working on too many things at once (narrow scope)
- The file is too large and needs refactoring (flag it)

### State Persistence
Use external tools for state:
- **Todo lists** — Track progress without consuming context
- **File system** — Write summaries to temp files
- **Session state** — Use session variables for cross-turn data

---

## Context Anti-Patterns

| Anti-Pattern | Why It Hurts |
|---|---|
| **Including entire files** | Eats context budget; most of the file is irrelevant |
| **Repeating history** | Every turn doesn't need full conversation replay |
| **Loading unrelated skills** | Only load skills relevant to the current task |
| **Parallelizing dependent tasks** | Results in conflicts, wasted work, context pollution |
| **Never compacting** | Context degrades until the agent starts hallucinating or making mistakes |
| **Over-reading** | Reading 20 files when 3 would suffice |

---

## The Ultimate Rule

**Context is your most precious resource. Spend it wisely.**

Every byte of context should directly contribute to producing correct, high-quality output. If it doesn't, remove it.
