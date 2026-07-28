#!/usr/bin/env python3
"""Normalize Memory Hive raw learnings to the current lint schema.

Safe transforms only:
- add missing `confidence: medium` to YAML frontmatter
- add a first H1 derived from existing content/context/filename when missing
- rename files in-place to `<date>-<slug>.md` when they do not match lint convention

Does not move files between agent directories and does not overwrite existing files.
"""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from datetime import date

_hive = os.environ.get("MEMORY_HIVE_DIR") or (Path.home() / ".memory-hive")
RAW = Path(_hive).expanduser().resolve() / "hive" / "learnings" / "raw"
FILENAME_RE = re.compile(r'^\d{4}-[01]\d-[0-3]\d-.+[a-z0-9]\.md$')
DATE_RE = re.compile(r'\d{4}-[01]\d-[0-3]\d')


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[`*_~#>\[\]()]', '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s[:96].strip('-') or 'learning'


def title_case_slug(slug: str) -> str:
    words = [w for w in re.split(r'[-_\s]+', slug) if w]
    small = {'a','an','and','as','at','but','by','for','from','in','into','of','on','or','the','to','vs','with'}
    out = []
    for i, w in enumerate(words[:14]):
        if i and w in small:
            out.append(w)
        elif w in {'api','cli','ui','ux','pwa','jwt','oauth','rls','pdf','png','svg','mcp','llm','tts','qa','ws','wsl','gpu'}:
            out.append(w.upper())
        else:
            out.append(w[:1].upper() + w[1:])
    return ' '.join(out) or 'Learning'


def split_frontmatter(text: str):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != '---':
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            return lines[: i + 1], lines[i + 1 :]
    return None


def field_value(fm_lines, key: str) -> str | None:
    pat = re.compile(rf'^\s*{re.escape(key)}\s*:\s*(.*)\s*$', re.I)
    for line in fm_lines[1:-1]:
        m = pat.match(line.rstrip('\n'))
        if m:
            val = m.group(1).strip().strip('"\'')
            return val
    return None


def has_field(fm_lines, key: str) -> bool:
    return field_value(fm_lines, key) is not None


def body_has_h1(body_lines) -> bool:
    return any(re.match(r'^#\s+', line) for line in body_lines)


def first_content_title(body_lines, context: str | None, path: Path) -> str:
    for line in body_lines:
        s = line.strip()
        if not s or s.startswith('```') or s.startswith('---'):
            continue
        s = re.sub(r'^[-*+]\s+', '', s)
        s = re.sub(r'^\d+[.)]\s+', '', s)
        s = re.sub(r'^#+\s+', '', s)
        s = re.sub(r'\s+', ' ', s).strip()
        if len(s) >= 18:
            # First sentence/phrase, but don't leave markdown cruft.
            cut = re.split(r'(?<=[.!?])\s+', s)[0]
            cut = cut.strip(' -:')
            if len(cut) > 90:
                cut = cut[:90].rsplit(' ', 1)[0]
            return cut[:1].upper() + cut[1:]
    if context:
        c = re.sub(r'\s+', ' ', context).strip()
        if len(c) > 90:
            c = c[:90].rsplit(' ', 1)[0]
        return c[:1].upper() + c[1:]
    stem = DATE_RE.sub('', path.stem)
    return title_case_slug(slugify(stem))


def target_name(path: Path, fdate: str) -> str:
    if FILENAME_RE.match(path.name):
        return path.name
    stem = path.stem
    stem = DATE_RE.sub('', stem)
    stem = re.sub(r'^[-_]+|[-_]+$', '', stem)
    slug = slugify(stem)
    return f'{fdate}-{slug}.md'


def unique_path(parent: Path, name: str, current: Path) -> Path:
    cand = parent / name
    if cand == current or not cand.exists():
        return cand
    stem = cand.stem
    suffix = cand.suffix
    i = 2
    while True:
        cand = parent / f'{stem}-{i}{suffix}'
        if cand == current or not cand.exists():
            return cand
        i += 1


def normalize_file(path: Path, dry_run: bool = False):
    text = path.read_text(errors='replace')
    parsed = split_frontmatter(text)
    if not parsed:
        return {'path': str(path), 'skipped': 'missing_or_bad_frontmatter'}
    fm, body = parsed
    changed = []

    if not has_field(fm, 'confidence'):
        # Insert before closing delimiter.
        fm.insert(len(fm) - 1, 'confidence: medium\n')
        changed.append('confidence')

    if not body_has_h1(body):
        context = field_value(fm, 'context')
        title = first_content_title(body, context, path)
        # Ensure exactly one blank after frontmatter, then H1, then one blank before old body.
        while body and not body[0].strip():
            body.pop(0)
        body = [f'\n# {title}\n', '\n'] + body
        changed.append('h1')

    new_text = ''.join(fm + body)
    if new_text != text:
        changed.append('content') if 'content' not in changed else None
        if not dry_run:
            path.write_text(new_text)

    fdate = field_value(fm, 'date') or str(date.today())
    if not DATE_RE.fullmatch(fdate):
        # Leave bad date for lint to report; do not invent date unless missing.
        fdate = str(date.today())
    new_name = target_name(path, fdate)
    new_path = unique_path(path.parent, new_name, path)
    if new_path != path:
        changed.append(f'rename->{new_path.name}')
        if not dry_run:
            path.rename(new_path)

    return {'path': str(path), 'new_path': str(new_path), 'changed': changed}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    results = []
    for path in sorted(RAW.rglob('*.md')):
        if path.name == 'README.md' or path.name.startswith('.'):
            continue
        results.append(normalize_file(path, args.dry_run))
    changed = [r for r in results if r.get('changed')]
    skipped = [r for r in results if r.get('skipped')]
    print(f'scanned={len(results)} changed={len(changed)} skipped={len(skipped)} dry_run={args.dry_run}')
    for r in changed[:250]:
        print(f"- {r['path']} -> {r.get('new_path', r['path'])}: {', '.join(r['changed'])}")
    if len(changed) > 250:
        print(f'... {len(changed)-250} more changed files omitted')
    if skipped:
        print('skipped:')
        for r in skipped[:50]:
            print(f"- {r['path']}: {r['skipped']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
