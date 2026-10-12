# Factory

This project runs the z-sdlc software factory: issue-driven agent stages on self-hosted runners, as
the `factory` bundle installs them. The rules are `[sdlc-root]/process/factory.md` (D1 stage contract,
D2 credential boundary, D3 planning tier, D4 production tier, D5 improve loop); what to set up before
the first run is its Enablement section.

**The factory workflows are rendered.** Each `.github/workflows/factory-*.yml` is `.github/factory/templates/<same
name>` with this project's settings (`factory.json`, and `planning.json`'s database) put in by
`render.py`. Edit the settings and run `python3 .github/factory/render.py`; CI's
`render.py --check` refuses a workflow edited by hand. Templates, scripts, guards and the stack
profile come from z-sdlc and are refreshed by `sdlc-migrate`; change them there.

## Operating notes

This file is the project's: record its runners, hosts, environments and anything else an operator
needs here. `sdlc-migrate` never overwrites it.
