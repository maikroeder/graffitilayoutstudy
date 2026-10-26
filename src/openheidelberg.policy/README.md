# openheidelberg.policy

Policy package of the OpenHeidelberg site, built the way `graffiti.policy` is: installing it installs
everything the site needs.

- `profiles/default/metadata.xml` depends on `graffiti.policy` (which installs the Graffiti packages and the
  Interaktiv tiles editor packages) and on `openheidelberg.tile_card`.
- `profiles/uninstall` and `setuphandlers.uninstall` uninstall the same products again. Keep the list in
  `setuphandlers.py` in sync with `metadata.xml`.
- `upgrades/` holds the upgrade steps; the profile version is in `metadata.xml`.

Where the site layout (design tokens, tile page layouts) will live is open until the design guidelines are
provided.

Status: skeleton only. Unlike `graffiti.policy` there is no `testing.py` yet; Graffiti's tests import
`GraffitiTestingLayer` from `graffiti.testing.testing`, which is not part of this repository.
