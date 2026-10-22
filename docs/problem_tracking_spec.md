# SCM Problem Tracking Specification

## Purpose
Defines defect reporting, anomaly tracking, and resolution mapping to formal Change Requests.

## Problem Tracking Workflow
1. Incident Detection: Anomaly reported during testing, staging, or FCA/PCA audit.
2. Problem Record Creation: Problem Report (PR) logged with severity (Critical, High, Medium, Low).
3. Root Cause Analysis: Correlate anomaly with historical failures in Organizational Memory.
4. Corrective Action: Spawn a Change Request (CR) targeting the affected Configuration Item.
5. Verification & Closure: Run automated regression suite; close PR upon CR verification.
