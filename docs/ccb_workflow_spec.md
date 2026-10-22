# SCM Change Management & CCB Workflow Specification

## Purpose
Defines the state transition lifecycle for Configuration Change Requests (CRs) under Change Control Board (CCB) governance.

## State Transition Pipeline
Draft -> Submitted -> Under Evaluation -> Pending Review -> Approved/Rejected -> Implemented -> Tested -> Closed

## Gate Criteria
1. Proposal Gate: Requires affected CI identifier, risk level, business impact, and concrete diff.
2. Trust Evaluation Gate: Adaptive trust engine computes score (0-100) and confidence.
3. CCB Adjudication Gate: Human-in-the-loop review by authorized Project Manager or Configuration Manager.
4. Archival Gate: Tested outcomes are archived into Organizational Memory for institutional learning.
