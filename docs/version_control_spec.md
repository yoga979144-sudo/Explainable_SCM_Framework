# SCM Version Management Specification

## Purpose
Defines the version progression and baseline rules for all Configuration Items (CIs) in the framework.

## Version Numbering Schema
* Major.Minor (e.g., 1.0 -> 1.1 -> 2.0)
* Major: Architectural change, schema overhaul, or critical breaking modification.
* Minor: Backward-compatible parameter tuning, feature additions, or bug patches.

## Verification Gate
Before a version is promoted to Baselined status:
1. Automated diff must be generated and inspected.
2. Formal CCB approval must be recorded.
3. Automated regression tests must complete with 100% pass rate.
