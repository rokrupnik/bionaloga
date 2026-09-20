#!/usr/bin/env python3
"""Postpone a task, and wake it when its time comes.

    python3 scripts/waiting.py postpone T-26-190 26-W39 --by Rok --note "po sejmu"
    python3 scripts/waiting.py postpone 190 2026-09-25
    python3 scripts/waiting.py wake [--dry-run] [--push] [--json]

`postpone` sets `status: waiting`, writes the target into `until:` (a week
`YY-Wnn` or a date `YYYY-MM-DD`), moves the file into that week's folder and
commits. `wake` runs once a day (the bot on the server, cron on a laptop):
every `waiting` task whose `until:` has arrived goes back to `open`, so the
usual planning picks it up. A `waiting` task without `until:` waits for a
person. Stdlib only; the task file stays the only record.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS = os.path.join(ROOT, 'work', 'tasks')
WEEK_RX = re.compile(r'^(?:(\d{2})-)?W(\d{1,2})$', re.I)
DATE_RX = re.compile(r'^\d{4}-\d{2}-\d{2}$')
ID_RX = re.compile(r'^(?:T-(\d{2})-)?(\d{1,3})$', re.I)


def git(*args: str) -> str:
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f'git {" ".join(args)}: {r.stderr.strip() or r.stdout.strip()}')
    return r.stdout


def task_files() -> list[str]:
    out = []
    if not os.path.isdir(TASKS):
        return out
    for week in sorted(os.listdir(TASKS)):
        d = os.path.join(TASKS, week)
        if os.path.isdir(d):
            out += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith('.md')]
    return out


def field(text: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:[ \t]*([^#\n]*?)[ \t]*(?:#.*)?$', frontmatter(text), re.M)
    return (m.group(1) if m else '').strip()


def frontmatter(text: str) -> str:
    m = re.match(r'^---\n(.*?)\n---', text, re.S)
    return m.group(1) if m else ''


def set_field(text: str, key: str, value: str) -> str:
    """Set `key:` inside the frontmatter, keep a trailing comment, insert after
    `status:` when the key is missing."""
    head, sep, body = text.partition('\n---')
    if not text.startswith('---'):
        raise SystemExit('task file without frontmatter')
    rx = re.compile(rf'^({re.escape(key)}:)[ \t]*[^#\n]*?[ \t]*(#.*)?$', re.M)
    if rx.search(head):
        head = rx.sub(lambda m: f'{m.group(1)} {value}'.rstrip() + (f'  {m.group(2)}' if m.group(2) else ''), head, count=1)
    else:
        head = re.sub(r'^(status:.*)$', rf'\1\n{key}: {value}'.rstrip(), head, count=1, flags=re.M)
    return head + sep + body


def note(text: str, line: str) -> str:
    if '## Result' not in text:
        text = text.rstrip() + '\n\n## Result\n'
    return text.rstrip() + '\n\n' + line.strip() + '\n'


def find(task_ref: str) -> tuple[str, str]:
    """('T-26-190', path) from 'T-26-190' or '190' (this year's prefix)."""
    m = ID_RX.match(task_ref.strip())
    if not m:
        raise SystemExit(f'not a task id: {task_ref}')
    yy = m.group(1) or f'{dt.date.today().year % 100:02d}'
    tid = f'T-{yy}-{int(m.group(2)):03d}'
    hits = [p for p in task_files() if re.match(rf'^(x_)?{tid}_', os.path.basename(p))]
    if not hits:
        raise SystemExit(f'{tid}: no task file')
    return tid, hits[0]


def week_of(day: dt.date) -> str:
    y, w, _ = day.isocalendar()
    return f'{y % 100:02d}-W{w:02d}'


def parse_until(raw: str, yy_hint: str) -> tuple[str, str]:
    """('26-W39', '26-W39') for a week, ('2026-09-25', '26-W39') for a date:
    the value to store and the week folder it lands in."""
    raw = raw.strip()
    if DATE_RX.match(raw):
        d = dt.date.fromisoformat(raw)
        return raw, week_of(d)
    m = WEEK_RX.match(raw)
    if m:
        wk = f'{m.group(1) or yy_hint}-W{int(m.group(2)):02d}'
        return wk, wk
    raise SystemExit(f'until must be YY-Wnn, Wnn or YYYY-MM-DD, not {raw!r}')


def due(until: str, today: dt.date) -> bool:
    if DATE_RX.match(until):
        return today >= dt.date.fromisoformat(until)
    m = WEEK_RX.match(until)
    if not m:
        return False
    y, w, _ = today.isocalendar()
    return (y % 100, w) >= (int(m.group(1) or y % 100), int(m.group(2)))


def postpone(a: argparse.Namespace) -> int:
    tid, path = find(a.task)
    text = open(path, encoding='utf-8').read()
    status = field(text, 'status')
    if status == 'done':
        raise SystemExit(f'{tid} is done; nothing to postpone')
    until, week = parse_until(a.until, tid.split('-')[1])
    text = set_field(text, 'status', 'waiting')
    text = set_field(text, 'until', until)
    text = set_field(text, 'week', week)
    who = f' ({a.by})' if a.by else ''
    text = note(text, f'Odloženo {dt.date.today().isoformat()}{who}: do {until}, prej `{status}`.' + (f' {a.note}' if a.note else ''))
    new_dir = os.path.join(TASKS, week)
    os.makedirs(new_dir, exist_ok=True)
    new_path = os.path.join(new_dir, os.path.basename(path))
    open(path, 'w', encoding='utf-8').write(text)
    if not a.no_commit:
        if new_path != path:
            git('mv', os.path.relpath(path, ROOT), os.path.relpath(new_path, ROOT))
        git('add', os.path.relpath(new_path, ROOT))
        git('commit', '-q', '-m', f'work: {tid} waiting until {until}' + (f' ({a.by})' if a.by else ''))
    elif new_path != path:
        os.replace(path, new_path)
    print(json.dumps({'id': tid, 'until': until, 'week': week, 'path': os.path.relpath(new_path, ROOT), 'was': status}))
    return 0


def wake(a: argparse.Namespace) -> int:
    today = dt.date.today()
    if a.push and not a.dry_run:
        git('pull', '-q', '--rebase', '--autostash')
    woken = []
    for path in task_files():
        text = open(path, encoding='utf-8').read()
        if field(text, 'status') != 'waiting':
            continue
        until = field(text, 'until')
        if not until or not due(until, today):
            continue
        tid = field(text, 'task')
        woken.append({'id': tid, 'until': until, 'title': field(text, 'title'), 'path': os.path.relpath(path, ROOT)})
        if a.dry_run:
            continue
        text = set_field(text, 'status', 'open')
        text = set_field(text, 'until', '')
        text = note(text, f'Zbujeno {today.isoformat()}: rok `{until}` je tu, nazaj v `open`.')
        open(path, 'w', encoding='utf-8').write(text)
        git('add', os.path.relpath(path, ROOT))
        git('commit', '-q', '-m', f'work: {tid} open (waited until {until})')
    if a.push and woken and not a.dry_run:
        git('push', '-q')
    if a.json:
        print(json.dumps(woken))
    else:
        for w in woken:
            print(f'{w["id"]} {w["title"]} — {"would wake" if a.dry_run else "open"} (until {w["until"]})')
        if not woken:
            print('nothing due')
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('postpone', help='status waiting, until <week|date>, file into that week')
    p.add_argument('task'); p.add_argument('until')
    p.add_argument('--by', default=''); p.add_argument('--note', default='')
    p.add_argument('--no-commit', action='store_true')
    p.set_defaults(fn=postpone)
    w = sub.add_parser('wake', help='waiting tasks whose until has arrived → open')
    w.add_argument('--dry-run', action='store_true'); w.add_argument('--push', action='store_true')
    w.add_argument('--json', action='store_true')
    w.set_defaults(fn=wake)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
