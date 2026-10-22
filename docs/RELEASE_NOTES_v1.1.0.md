# Release Notes: SCM Framework v1.1.0

## Release Title
**SCM Framework v1.1.0 — Adaptive Trust Threshold Optimization (CR-001)**

* **Tag:** `v1.1.0`
* **Target Commit:** `101d450` (Merge commit of `feature/trust-learning`)
* **Date:** October 2026
* **Academic Review Milestone:** Review 3 Change Demonstration

---

## 1. Summary of Changes

This release incorporates Change Request **CR-001** (*CONFIGURATION TRUST THRESHOLD CHANGE*):
* **Affected Artifact:** `CI-006` (`config/trust_engine_params.json`).
* **Previous Value:** `trust_threshold = 70`.
* **New Value:** `trust_threshold = 80`.
* **Justification:** Raised the minimum acceptance threshold for automated trust evaluation based on historical precedents `MEM-001` and `MEM-002`, eliminating unverified configuration deployments while maintaining pipeline throughput.
* **Governance Approval:** Formal CCB review approval recorded by Project Manager `yogalakshmi`.
* **Testing Status:** Verified by QA automated regression suite (35 passed assertions, 0 defects).

---

## 2. Git Version Differential

```diff
diff --git a/config/trust_engine_params.json b/config/trust_engine_params.json
index 187d702..5830b3e 100644
--- a/config/trust_engine_params.json
+++ b/config/trust_engine_params.json
@@ -1,8 +1,8 @@
 {
   "ci_id": "CI-006",
   "name": "Trust Evaluation Configuration",
-  "version": "1.0",
-  "trust_threshold": 70,
+  "version": "1.1",
+  "trust_threshold": 80,
   "confidence_min_samples": 2,
   "penalty_risk_high": 14,
   "enable_memory_retrieval": true,
```

---

## 3. How to Publish on GitHub

1. Push commit and tag:
   ```bash
   git push origin main
   git push origin v1.1.0
   ```
2. On GitHub, navigate to **Releases** &rarr; **Draft a new release**.
3. Choose tag `v1.1.0`.
4. Set title to: `SCM Framework v1.1.0`.
5. Paste these notes and click **Publish release**.
