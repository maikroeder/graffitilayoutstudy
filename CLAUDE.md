# graffitilayoutstudy — working agreement for Claude

Code for the *Graffiti Layout Study* paper. Paper: `~/Writing/GraffitiLayoutStudyPaper`.
Process record: `~/Writing/Workspaces/graffiti-layout-study-paper/description.md`.

1. Site-specific code lives only in `src/openheidelberg.*` packages. Never edit the vendored Graffiti
   packages (`src/graffiti.*`, `src/interaktiv.cronjob`, `src/interaktiv.workingcopy`; copied from Graffiti
   `main`) or the mr.developer checkouts `src/interaktiv.*` — they are upstream code. Refresh the vendored
   copy from a new Graffiti checkout instead and record the upstream commit in README.md.
2. The paper describes what was actually built. Record what ran and what did not (the buildout has not
   been run yet as of scaffolding); never describe intended behaviour as achieved.
3. Python style: no list/dict comprehensions (explicit loops), one import per line.
4. Do not commit unless asked; never commit straight to `main`.
