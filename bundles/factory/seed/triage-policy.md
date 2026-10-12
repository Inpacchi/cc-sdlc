# Triage policy

The project's half of factory triage: what `sdlc-triage` reads in step 3 besides the framework's
`CLAUDE.md` sections. The skill holds the rubric; this file holds what only this project knows. It
is the project's own file (the factory bundle seeds it once and never overwrites it), and CD reviews
it like any other agent instruction (`.github/` is code-owned).

## Direction

Where the project says what it is for and what comes next: a vision or roadmap file, or the
`CLAUDE.md` sections that hold its goals and current stage. Triage reads them to judge whether an
issue fits.

- (none yet: name the file or sections)

## Rules

The project's own `CLAUDE.md` sections triage applies, beyond the framework's: its approval list
(what needs CD's approval: dependencies, contracts, schemas and the like), and any data-integrity or
domain rules.

- (none yet)

## Containers

The project's deployable units and the paths each owns. Shared code counts for every container that
imports it; a change spanning more than one container is a plan trigger.

| Container | Paths |
|---|---|
| (name) | (paths) |

## Plan triggers

Beyond the framework's and the factory's own (live verification, the control plane, cross-container
scope): the code whose correctness an unattended run can't check, such as a data pipeline whose
constants must be sourced, money or pricing math, model training, or message shapes between
containers. Any one rules out `ready-for-dispatch`.

- (none yet)

## External sources

The services and documents whose behavior decisions turn on, and where to verify them (Context7
library or vendor IDs, official docs).

- (none yet)
