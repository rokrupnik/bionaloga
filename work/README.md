# `work/` — tasks

Everything about *what we are doing* lives here, as markdown in the repo, so
people and agents read the same files. One file per task, and that file is the
task's only source of truth — there is no tracker behind an API and no second
copy to keep in sync.

```
work/
  README.md              this file — the conventions
  TEMPLATE.md            copy it to start a task
  POLICY.md              what the operator bot may decide alone, and who it asks
  tasks/26-W37/          one file per task, grouped by ISO work week
  costs/                 one CSV per month: every model session, its cost (written by the bot)
  reports/               scheduled reports, one folder per report (written by the bot)
```

## Reading it: the `work` CLI

`work` (on `PATH`) is a read-only view over these files. Register the project
once with `work project add <path> <name>`; from inside the project:

```bash
work                    # the overview, grouped by owner
work --blocked          # blocked, needs-info, waits-info
work --notify           # shipped; the requester has not been told yet
work validate           # the conventions, checked
work next-id            # the next free task number
```

The bot reads `work --json`; nothing else parses task files.

## Task files

```
work/tasks/26-W37/T-26-001_short-slug@ROK.md
                  │      │   │          └── assignee(s), optional
                  │      │   └── slug
                  │      └── global counter, MAX + 1, never reused
                  └── YY of the year the task was created
```

- **Week folder** is `YY-W<ISO week>`. It records the week the task is
  *scheduled for*. A task that slips moves to the next week's folder; **its
  number never changes**, so durable references use only the ID.
- **Done is the `x_` prefix**: `x_T-26-001_…md`. Sorting puts finished tasks at
  the bottom; open work stays at the top. Keep `status:` and `completed:` in
  step with it.
- **Assignment is the `@NAME` suffix**; two owners is `@ROK+ANA`.
- Renaming is the state change. Use `git mv` so history follows the file.
- Refer to a task only by its ID (`T-26-001`), never by a path or a link.

### Frontmatter

```markdown
---
task: T-26-001
title: What changes for the user when this is done
status: open           # see "Task state"
assignee: [ROK]        # who does it
requested-by: Ana      # who asked for it — never empty
week: 26-W37
created: 2026-09-05
completed:             # set when status flips to done
notified:              # date the requester was told it shipped
blocked-by: []         # task ids only
visibility: team       # team | restricted (restricted → admin-only channel)
run-as:                # admin, once an admin approved elevated access
cost-usd:              # running total, written by the bot
---
```

**`requested-by` is deliberately separate from `assignee`.** It records who
wants the thing, so somebody knows who to go back to with a question and who to
tell when it ships.

### Task state

```text
open -> planning -> ready -> in-progress -> review -> notify -> done
from anywhere:  blocked | needs-info -> waits-info -> back to where it came from
```

- `open` — captured, not yet worked out.
- `planning` — the plan is being written into the task file.
- `ready` — the plan and every input are present; the bot may start.
- `in-progress` — being executed.
- `review` — a `## Result` is present and wants a second pair of eyes.
- `blocked` — our move, and we cannot make it (technical obstacle, dependency).
- `needs-info` — an input or decision is missing and the person has not been
  asked yet. `waits-info` — they have been asked and owe an answer.
- `notify` — shipped and verified; the requester has not been told yet.
- `done` — finished, `completed:` set, filename starts with `x_`.

### How a task gets done

1. **The task is written first** — the ask, the context, why it matters.
2. **The plan goes into the same file** under `## Plan`: exact files, current
   vs. target state, how each step is verified. A fresh session must be able to
   execute it without the conversation that produced it.
3. **Execution appends `## Result`**: what shipped, what did not, commits.
4. **Deterministic checks** run after every deploy (the bot's `verify:` list).
5. **Closing**: rename to `x_…`, set `status: done` and `completed:`, tell
   whoever is in `requested-by`.

## Redact personal data before committing

Tasks grow out of support mail and customer data. Strip or anonymise names,
e-mail addresses, phone numbers, postal addresses and order ids that identify a
person (`[customer]`, `jane.doe@example.com`) **before** `git add`. Internal
identifiers that are not personal data — product ids, SKUs, company names —
stay. Purchase prices, margins and bank figures stay in the task file and never
go into a chat message.
