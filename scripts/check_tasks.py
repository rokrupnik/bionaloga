#!/usr/bin/env python3
"""Check that task files in `work/tasks/` agree with `work/README.md`.

A task is one file and that file is the only source of truth, so the
frontmatter must say what the filename says:
  1. the frontmatter parses and has every required field
  2. `task:` matches the number in the filename
  3. the `@OWNER` suffix matches `assignee`
  4. `status` is one of the allowed states
  5. `status: done` <-> `x_` prefix <-> `completed` set
  6. task numbers are unique
  7. every `blocked-by` points at an existing task
  8. `week:` matches the folder name
  9. dates are YYYY-MM-DD
 10. every relative markdown link under work/ resolves
 11. `requested-by` is not empty
Writes nothing, touches no network. Exit 0 = clean.

  python3 scripts/check_tasks.py
  CHECK_SELFTEST=1 python3 scripts/check_tasks.py   (must fail)
"""
import datetime
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, 'work')
TASKS = os.path.join(WORK, 'tasks')
SELFTEST = os.environ.get('CHECK_SELFTEST') == '1'

STATES = {'open', 'planning', 'ready', 'in-progress', 'review', 'integrating',
          'changes-requested', 'needs-info', 'waits-info', 'blocked', 'notify', 'done'}
REQUIRED = ('task', 'title', 'status', 'assignee', 'requested-by', 'week',
            'created', 'completed', 'blocked-by')
NAME = re.compile(r'^(x_)?T-(\d{2})-(\d{3})_([a-z0-9-]+?)(?:@([A-Z+]+))?\.md$')
WEEK = re.compile(r'^(x_)?(\d{2}-W\d{2})$')
LINK = re.compile(r'\[[^\]]*\]\(([^)#][^)]*)\)')
BROKEN = '''---
task: T-26-998
title: selftest
status: notify
assignee: [ROK]
requested-by:
week: 26-W01
created: 2026-13-99
completed: 2026-08-22
blocked-by: [T-26-777]
---
# selftest
[dead](never-existed.md)
'''


def frontmatter(txt):
    if not txt.startswith('---\n'):
        return None
    end = txt.find('\n---', 4)
    if end < 0:
        return None
    fm = {}
    for line in txt[4:end].splitlines():
        if not line or line.startswith('#') or line.startswith(' '):
            continue
        if ':' not in line:
            return None
        k, v = line.split(':', 1)
        v = v.split(' #')[0].strip()
        fm[k.strip()] = v
    return fm


def listed(value):
    v = value.strip()
    if v.startswith('[') and v.endswith(']'):
        v = v[1:-1]
    return [x.strip() for x in v.split(',') if x.strip()]


def is_date(v):
    try:
        datetime.date.fromisoformat(v)
        return True
    except ValueError:
        return False


def main():
    global TASKS
    tmp = None
    if SELFTEST:
        tmp = tempfile.mkdtemp()
        shutil.copytree(TASKS, os.path.join(tmp, 'tasks'), dirs_exist_ok=True)
        wk = os.path.join(tmp, 'tasks', '26-W01')
        os.makedirs(wk, exist_ok=True)
        with open(os.path.join(wk, 'T-26-998_selftest@ROK.md'), 'w') as f:
            f.write(BROKEN)
        TASKS = os.path.join(tmp, 'tasks')
    errors = []

    def err(where, msg):
        errors.append(f'ERROR {where}: {msg}')

    seen = {}
    files = []
    for folder in sorted(os.listdir(TASKS)) if os.path.isdir(TASKS) else []:
        wm = WEEK.match(folder)
        fdir = os.path.join(TASKS, folder)
        if not os.path.isdir(fdir):
            continue
        if not wm:
            err(folder, 'folder name is not YY-Wnn')
            continue
        for name in sorted(os.listdir(fdir)):
            if not name.endswith('.md'):
                continue
            files.append((folder, wm.group(2), name, os.path.join(fdir, name)))
    for folder, week, name, path in files:
        where = f'{folder}/{name}'
        m = NAME.match(name)
        if not m:
            err(where, 'filename is not [x_]T-YY-NNN_slug[@OWNER].md')
            continue
        done_prefix, yy, nnn, _slug, owners = m.groups()
        tid = f'T-{yy}-{nnn}'
        if tid in seen:
            err(where, f'{tid} is also {seen[tid]}')
        seen[tid] = where
        txt = open(path, encoding='utf-8').read()
        fm = frontmatter(txt)
        if fm is None:
            err(where, 'frontmatter does not parse')
            continue
        for k in REQUIRED:
            if k not in fm:
                err(where, f'missing field: {k}')
        if fm.get('task') != tid:
            err(where, f'task: {fm.get("task")} != filename {tid}')
        status = fm.get('status', '')
        if status not in STATES:
            err(where, f'unknown status {status!r}')
        if (status == 'done') != bool(done_prefix):
            err(where, 'status done and x_ prefix disagree')
        if status == 'done' and not fm.get('completed'):
            err(where, 'done without completed')
        if status != 'done' and fm.get('completed'):
            err(where, 'completed set but not done')
        assignees = listed(fm.get('assignee', ''))
        if owners and sorted(owners.split('+')) != sorted(a.upper() for a in assignees):
            err(where, f'@{owners} != assignee {assignees}')
        if fm.get('week') != week:
            err(where, f'week: {fm.get("week")} != folder {week}')
        for k in ('created', 'completed', 'notified'):
            v = fm.get(k, '')
            if v and not is_date(v):
                err(where, f'{k}: {v!r} is not YYYY-MM-DD')
        if not fm.get('requested-by'):
            err(where, 'empty requested-by')
        for dep in listed(fm.get('blocked-by', '')):
            if not re.match(r'^T-\d{2}-\d{3}$', dep):
                err(where, f'blocked-by {dep!r} is not a task id')
        fm['_deps'] = listed(fm.get('blocked-by', ''))
        for link in LINK.findall(txt):
            if '://' in link or link.startswith('mailto:'):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), link.split('#')[0]))
            if not os.path.exists(target):
                err(where, f'dead link {link}')
        for dep in fm['_deps']:
            if dep not in seen and not any(dep in n for _, _, n, _ in files):
                err(where, f'blocked-by {dep} does not exist')
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    for e in errors:
        print(e)
    print(f'{len(files)} tasks, {len(errors)} errors')
    if SELFTEST:
        sys.exit(0 if errors else 1)
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
