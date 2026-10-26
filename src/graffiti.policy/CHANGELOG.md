# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - YYYY-MM-DD
### Added
- Install graffiti.pdfcheck: checks PDF files on upload whether they can be processed later, upgrade step 0013 installs it on existing sites (ref #22774) [@mliebischer](https://code.interaktiv.de/mliebischer)
- Install the Graffiti tiles: the five placeholder tiles for entry pages and graffiti.tile_button, upgrade step 0012 installs them on existing sites (ref #22776) [@mliebischer](https://code.interaktiv.de/mliebischer)
### Changed
- License in setup.py is now BSD-3-Clause, as in LICENSE.md of the Graffiti repository [@mliebischer](https://code.interaktiv.de/mliebischer)
### Deprecated
### Removed
### Fixed
- Uninstall list: missing comma merged `graffiti.policy` and `graffiti.contenttypes` into one entry (ref #22776) [@mliebischer](https://code.interaktiv.de/mliebischer)
### Security
### Breaking Changes

## [1.0.1] - 2025-05-28
### Added
- Add upgrade step to install graffiti.contenttypes [@mliebischer](https://github.com/mliebischer)

## [1.0.0] - 2025-05-14
Initial release


