"""Read the deliverable catalog (docs/_index.md) and a split record's parts table.

Shared by implement_guard.py (checks a split PR's documents agree with the run's result) and
split_parts.py (files the parts of a merged split). Pure functions over markdown text; no I/O.
Format: ops/sdlc/process/deliverable_lifecycle.md § Dependencies and § Splitting a Deliverable,
ops/sdlc/templates/split_record_template.md.
"""

import re

ID = re.compile(r"^D\d+[a-z]?$")
PART_ID = re.compile(r"^D\d+[a-z]$")
TIERS = ("lite", "full")
NONE = {"", "—", "-", "–", "none"}
LINK = re.compile(r"^\[([^\]]+)\]\([^)]*\)$")
SPEC = re.compile(r"^docs/current_work/specs/d\d+[a-z]?_[a-z0-9_]+_spec\.md$")


def cells(line):
    """The cells of a markdown table row, stripped; None for a line that isn't a row."""
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        return None
    return [c.strip() for c in line[1:-1].split("|")]


def tables(text):
    """Every table as (header cells, [row cells...]), separator rows dropped."""
    out, header, rows = [], None, []
    for line in text.splitlines() + [""]:
        row = cells(line)
        if row is None:
            if header:
                out.append((header, rows))
            header, rows = None, []
        elif header is None:
            header = row
        elif not all(re.fullmatch(r":?-+:?", c) for c in row):
            rows.append(row)
    return out


def plain(cell):
    """A cell's text without a markdown link, backticks or surrounding space."""
    cell = cell.strip()
    m = LINK.match(cell)
    if m:
        cell = m.group(1)
    return cell.strip("`").strip()


def ids(cell):
    """Deliverable IDs in a Depends on cell (`D11a, D12`, or a dash for none). A token that isn't an
    ID raises ValueError, so a typo can't silently drop a dependency."""
    cell = plain(cell)
    if cell.lower() in NONE:
        return []
    out = []
    for token in (t.strip() for t in cell.split(",")):
        token = plain(token)
        if not ID.match(token):
            raise ValueError(f"not a deliverable ID: {token!r}")
        out.append(token)
    return out


def catalog_rows(text):
    """The active deliverables table, as {ID: {column: cell}}. Raises ValueError if it's missing."""
    for header, rows in tables(text):
        if header[:3] == ["ID", "Name", "Status"]:
            out = {}
            for row in rows:
                if len(row) != len(header):
                    raise ValueError(f"catalog row has {len(row)} cells, header has {len(header)}: {row[:1]}")
                out[plain(row[0])] = dict(zip(header, row))
            return out
    raise ValueError("no catalog table whose header starts | ID | Name | Status |")


def split_parts(text):
    """The parts table of a split record, in order, as dicts with part, name, tier, depends_on, spec
    and scope. Raises ValueError on a missing table or a malformed row."""
    for header, rows in tables(text):
        if header[:3] == ["Part", "Name", "Tier"]:
            need = ["Part", "Name", "Tier", "Depends on", "Spec", "Scope"]
            if header != need:
                raise ValueError(f"parts table columns must be {need}")
            parts = []
            for row in rows:
                if len(row) != len(need):
                    raise ValueError(f"parts row has {len(row)} cells: {row[:1]}")
                r = dict(zip(need, row))
                spec = plain(r["Spec"])
                parts.append({"part": plain(r["Part"]), "name": plain(r["Name"]), "tier": plain(r["Tier"]).lower(),
                              "depends_on": ids(r["Depends on"]), "spec": "" if spec.lower() in NONE else spec,
                              "scope": r["Scope"].strip()})
            return parts
    raise ValueError("no parts table (header | Part | Name | Tier | ...)")


def check_parts(parent, parts):
    """The rules every split's parts follow. Returns nothing; raises ValueError naming the first break."""
    if not ID.match(parent) or not re.fullmatch(r"D\d+", parent):
        raise ValueError(f"a split parent must be a top-level ID (Dnn), not {parent!r}")
    if not 2 <= len(parts) <= 6:
        raise ValueError("a split has 2 to 6 parts")
    seen = []
    for i, p in enumerate(parts):
        want = f"{parent}{chr(ord('a') + i)}"
        if p["part"] != want:
            raise ValueError(f"part {i + 1} must be {want}, in order (got {p['part']!r})")
        if p["tier"] not in TIERS:
            raise ValueError(f"{want}: tier must be lite or full")
        if not p["name"].strip() or not p["scope"].strip():
            raise ValueError(f"{want}: needs a name and a scope")
        for d in p["depends_on"]:
            if d == want or d == parent:
                raise ValueError(f"{want} can't depend on itself or its parent")
            if re.fullmatch(rf"{parent}[a-z]", d) and d not in seen:
                raise ValueError(f"{want} depends on {d}, which isn't an earlier part (parts are in execution order)")
        if p["spec"]:
            if p["tier"] != "full":
                raise ValueError(f"{want}: only a full-tier part reuses a spec")
            if not SPEC.match(p["spec"]):
                raise ValueError(f"{want}: spec must be a docs/current_work/specs/dNN_name_spec.md path")
        seen.append(want)
