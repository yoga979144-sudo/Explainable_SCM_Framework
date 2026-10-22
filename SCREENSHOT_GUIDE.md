# SCM Framework - Review 3 Screenshot Demonstration Guide

**Project Title:** Explainable Organizational Memory-Driven SCM Framework Using Adaptive Configuration Trust Learning  
**Institution:** Final Year Academic Project (Review 3 Milestone)  
**Authors:**
1. **YOGALAKSHMI S** (23MIS0383)
2. **PAVITHRA L** (23MIS0160)
3. **YUVARAJ G** (24MIS0403)

---

## 1. Overview of Included Implementation Screenshots

All screenshots in this directory are captured directly from the live running web application running at `http://127.0.0.1:5000`. They demonstrate full-stack functionality across all 15 project modules.

| Screenshot Filename | SCM Module | What it Demonstrates & Evidence for Review 3 |
| :--- | :--- | :--- |
| `01_login_page.png` | **Module 1: Authentication & RBAC** | Demonstrates the 6 stakeholder roles (Project Manager, Configuration Manager, Developer, QA Engineer, DevOps Engineer, ML/Trust Analyst) and student demo accounts with secure hashed authentication. |
| `02_dashboard.png` | **Module 2: Operations Dashboard** | Real-time database metrics: 12 CIs, pending CRs, average trust score (84.0/100), Chart.js trust distribution chart, CI category breakdown, and live activity feed. |
| `03_configuration_items.png` | **Module 3: Configuration Identification** | Catalog of 12 Configuration Items spanning all 10 required SCM categories (Source Code, Requirements, Schemas, ML Models, etc.) with filter and search controls. |
| `04_configuration_detail.png` | **Module 3: CI Detail & Traceability** | Inspection of CI-006 (Trust Evaluation Configuration) showing metadata, version progression, and incoming/outgoing traceability links. |
| `05_traceability_matrix.png` | **Module 3: Traceability View** | Multi-stage lifecycle flow mapping SRS Requirements &rarr; Source Code &rarr; Automated Tests &rarr; Configurations &rarr; Release Bundles. |
| `06_version_history.png` | **Module 4: Version Control** | Application-level version ledger with timestamps and descriptions, plus detection of local Git repository commits and architectural separation notice. |
| `07_version_comparator.png` | **Module 4: Differential Comparator** | Side-by-side visual difference table and unified diff output comparing Version 1.0 vs Version 1.1 of CI-006 (`trust_threshold = 70` &rarr; `80`). |
| `08_change_requests.png` | **Module 5: Change Management** | Comprehensive Change Request queue showing risk levels, business impact ratings, trust score badges, and lifecycle gate status. |
| `09_change_detail_review.png` | **Module 5 & 9: CR Detail & CCB Review** | **Core Academic Scenario (CR-001):** Displays proposed payload, trust evaluation summary (84.0/100), and interactive CCB approval ruling interface. |
| `10_organizational_memory.png` | **Module 6: Organizational Memory** | Institutional repository of 8 historical configuration changes showing past trust scores, test results, and implementation outcomes (Success, Failure, Rollback). |
| `11_similarity_retrieval.png` | **Module 6: TF-IDF Similarity Tool** | Live semantic similarity retrieval using scikit-learn TF-IDF vectorization and cosine distance to match proposed changes against past precedents. |
| `12_trust_evaluation_engine.png` | **Module 7: Adaptive Trust Engine** | Mathematical formulation card, active model weights (`v1.0-adaptive-rules`), and adaptive parameter tuning controls. |
| `13_explainability_panel.png` | **Module 8: Explainable AI Diagnostics** | **Primary Evaluation Artifact:** Full factor decomposition showing positive drivers, risk penalties, quantitative points breakdown, and cited precedents for CR-001. |
| `14_ccb_review_queue.png` | **Module 9: CCB Governance Queue** | Change Control Board review queue showing pending changes requiring formal human-in-the-loop board adjudication. |
| `15_status_accounting.png` | **Module 10: Status Accounting** | Real-time CSA ledger tracking CI identifiers, frozen versions, owners, lifecycle states, approval states, and baseline states with summary counters. |
| `16_baselines_management.png` | **Module 11: Configuration Baselines** | Authorized baselines (BL-001, BL-002) freezing approved sets of CI versions with approval governance rules. |
| `17_releases_management.png` | **Module 11: Release Management** | Packaging software releases (REL-001, REL-002) linked to baselines and verified change requests. |
| `18_fca_audit.png` | **Module 12: Functional Audit (FCA)** | 6-item formal FCA checklist evaluation verifying requirements mapping, defect resolution, and automated test completions. |
| `19_pca_audit.png` | **Module 12: Physical Audit (PCA)** | 7-item formal PCA checklist evaluation verifying code SHA-256 tree matches, build artifacts, schema integrity, and model tags. |
| `20_github_integration.png` | **Module 13: SCM Tool Integration** | Review 3 mandatory 4-feature integration matrix: Git Version Control, GitHub Issues mapping, Pull Request review, and GitHub Actions CI/CD. |
| `21_scm_standards.png` | **Module 14: SCM Standards** | Academic compliance mapping to IEEE/SWEBOK v3.0, CMMI-DEV v2.0, ITIL v4, and ISO/IEC/IEEE 12207. |
| `22_reports_export.png` | **Module 15: Reports & CSV Export** | Multi-tab analytical reports center supporting one-click CSV downloads for all 9 SCM ledgers. |

---

## 2. Review 3 Demonstration Narrative

When demonstrating this project to the review committee or professor:

1. **Step 1 - Login & RBAC:** Open `01_login_page.png`. Point out the 6 stakeholder roles and 1-click role switcher. Log in as Project Manager (`yogalakshmi`) or Configuration Manager (`pavithra`).
2. **Step 2 - Executive Overview:** Open `02_dashboard.png`. Highlight that all metrics (12 CIs, 8 memory items, pending CRs, average trust score) are dynamically computed from SQLite.
3. **Step 3 - The Core Demonstration Scenario (CR-001):**
   - Open `09_change_detail_review.png` & `13_explainability_panel.png`.
   - Explain: *"A change was proposed to raise the trust threshold from 70 to 80 on CI-006. The system retrieved 3 similar past threshold modifications from Organizational Memory, noted that previous conservative increments succeeded while extreme jumps failed, computed an adaptive trust score of 84.0/100, cited the exact precedents, and recommended approval review."*
4. **Step 4 - Governance Workflow:** Demonstrate CCB approval &rarr; Developer implementation (incrementing CI-006 to v1.1) &rarr; QA automated test execution &rarr; Archival back into Organizational Memory.
5. **Step 5 - Audits & Standards:** Show `18_fca_audit.png` (Functional Audit) and `19_pca_audit.png` (Physical Audit) showing honest objective checklist calculations.
6. **Step 6 - Tool Integration:** Show `20_github_integration.png` showing the 4 Review 3 Git/GitHub features.
