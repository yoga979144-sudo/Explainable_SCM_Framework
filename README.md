# Explainable Organizational Memory-Driven SCM Framework Using Adaptive Configuration Trust Learning

A full-stack, enterprise-grade Software Configuration Management (SCM) web application integrating **adaptive configuration trust learning**, **organizational memory retrieval**, and **explainable AI decision support** for configuration changes, Change Control Board (CCB) governance, status accounting, and formal configuration audits.

---

## Academic Project Information

* **Project Title:** Explainable Organizational Memory-Driven SCM Framework Using Adaptive Configuration Trust Learning
* **Degree / Institution:** Final Year Academic Project (Review 3 Milestone)
* **Team Members:**
  1. **YOGALAKSHMI S** (Reg. No: `23MIS0383`) - Project Manager & Governance Lead
  2. **PAVITHRA L** (Reg. No: `23MIS0160`) - Configuration Manager & Baseline Lead
  3. **YUVARAJ G** (Reg. No: `24MIS0403`) - Developer & Trust Learning Specialist

---

## 1. Problem Statement

Traditional Software Configuration Management (SCM) systems (such as Git, SVN, Perforce, and GitHub) excel at file-level version control, delta storage, branching, and pull request tracking. However, they lack:
1. **Organizational Memory Integration:** Past configuration errors, rollbacks, and lessons learned are typically trapped in unindexed post-mortem notes or tickets, leading organizations to repeatedly commit similar dangerous configuration mistakes.
2. **Automated Risk & Trust Calibration:** Reviewers must manually assess complex configuration drifts (such as database connection pools, memory limits, and trust thresholds) without predictive reliability estimates.
3. **Explainable Decision Recommendations:** When changes are flagged or evaluated, reviewers require human-interpretable explanations detailing *why* a change is risky or safe, supported by concrete historical precedents.

This framework closes this gap by combining traditional SCM functions (identification, versioning, status accounting, audits, and baselines) with an **adaptive configuration trust learning engine** and an **explainable decision support system**.

---

## 2. Technology Stack

* **Backend:** Python 3.10+, Flask 3.1
* **Database & ORM:** SQLite, Flask-SQLAlchemy 3.1, SQLAlchemy 2.0
* **Machine Learning & Text Analytics:** Scikit-Learn 1.7 (TF-IDF Vectorization & Cosine Similarity)
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3, FontAwesome 6
* **Visualizations:** Chart.js 4.4 (dynamic trust distribution and CI category charts)
* **Testing:** Pytest 9.1, Flask Test Client (22 comprehensive automated tests)
* **SCM & CI/CD Tool Integration:** Git local integration, GitHub Issues mapping, GitHub Pull Request CCB workflow, and GitHub Actions (`.github/workflows/tests.yml`)
* **Environment:** 100% locally executable on Windows without external cloud services or paid APIs.

---

## 3. High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USER / CCB INTERFACE                            │
│  Bootstrap 5.3 + Chart.js + Visual Diff Comparator + Explainability    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST
┌───────────────────────────────────▼────────────────────────────────────┐
│                        FLASK APPLICATION ROUTING                       │
│  Auth (RBAC) │ Dashboard │ CIs │ CRs │ Memory │ Audits │ SCM │ Reports │
└─────────────────┬─────────────────────────────────┬────────────────────┘
                  │                                 │
┌─────────────────▼───────────────┐ ┌───────────────▼────────────────────┐
│      CORE SCM SERVICES          │ │     ADAPTIVE TRUST & AI ENGINE     │
│ • Configuration Identification  │ │ • TF-IDF Similarity Matcher        │
│ • Version History & Visual Diff │ │ • Multi-Factor Trust Formula       │
│ • Status Accounting Ledger      │ │ • Transparent Factor Decomposition │
│ • Baselines & Release Control   │ │ • Organizational Memory Feedback   │
│ • FCA / PCA Audit Engine        │ │ • Model Versioning & Param Tuning  │
└─────────────────┬───────────────┘ └───────────────┬────────────────────┘
                  │                                 │
┌─────────────────▼─────────────────────────────────▼────────────────────┐
│                   SQLITE RELATIONAL DATABASE                           │
│  Users │ CIs │ Versions │ Dependencies │ CRs │ History │ Memory        │
│  TrustEvaluations │ ModelVersions │ Audits │ Baselines │ Releases      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Complete Application Modules

The application implements all 15 required modules:

1. **Module 1: Login and Role Management (RBAC)**
   - 6 Stakeholder Roles: *Project Manager*, *Configuration Manager*, *Developer*, *QA Engineer*, *DevOps Engineer*, and *ML/Trust Analyst*.
   - Password hashing using Werkzeug PBKDF2 with SHA-256.
   - 1-click quick-login role switcher for fast evaluation and testing.
2. **Module 2: Real-Time Operations Dashboard**
   - Live KPI counters: Total CIs, Approved CIs, Pending CRs, Average Trust Score, Memory Precedents, and Pending Audits.
   - Dynamic Chart.js visualizations (Trust Score Doughnut Chart and CI Category Horizontal Bar Chart).
   - Academic demonstration scenario callout card (CR-001) and live activity feed.
3. **Module 3: Configuration Identification (CI Management)**
   - Catalog supporting 10 standard SCM categories: *Source Code*, *Requirement Documents*, *Design Documents*, *Test Cases*, *Build Scripts*, *Configuration Files*, *Deployment Scripts*, *Database Schemas*, *Machine Learning Models*, and *Organizational Knowledge Repository*.
   - Unique identifiers (`CI-001`, `CI-002`...).
   - Bidirectional dependency tracking and full-lifecycle traceability matrix.
4. **Module 4: Version Control and Visual Comparator**
   - Application-level configuration version progression (`v1.0` &rarr; `v2.0` &rarr; `v2.1`).
   - Side-by-side colorized visual HTML difference viewer and raw unified diff (`diff -u`) console.
   - Local Git check verifying whether Git is installed and displaying local commits while clearly explaining database vs Git version control.
5. **Module 5: Change Request (CR) Management**
   - Full change proposal specification: Title, Affected CI, Risk Level (Low/Med/High/Critical), Business Impact, and Proposed Configuration Diff.
   - Formal status transitions: `Draft` &rarr; `Submitted` &rarr; `Under Evaluation` &rarr; `Pending Review` &rarr; `Approved`/`Rejected` &rarr; `Implemented` &rarr; `Tested` &rarr; `Closed`.
   - Immutable audit trail in `ChangeRequestHistory`.
6. **Module 6: Organizational Memory Repository**
   - Institutional repository of historical changes with recorded test results, rollbacks, and empirical lessons learned.
   - Semantic similarity matching using scikit-learn TF-IDF cosine similarity.
   - Interactive similarity retrieval diagnostic tool.
7. **Module 7: Adaptive Configuration Trust Learning**
   - Multi-factor mathematical scoring formula computing trust from 0 to 100.
   - Separation of Trust Score, Evidence Confidence, and Recommendations.
   - Model versioning (`v1.0-adaptive-rules`) and interactive parameter tuning.
8. **Module 8: Explainable AI (XAI) & Diagnostics**
   - Positive trust drivers (points added) and risk penalty drivers (points deducted).
   - Cited historical precedents with match percentages.
   - Actionable next steps and factor contribution score table.
9. **Module 9: Change Review & CCB Governance**
   - Dedicated Change Control Board (CCB) review queue.
   - Board actions: *Approve*, *Reject*, *Request Modification*.
   - Enforces human-in-the-loop governance (high trust score does not bypass CCB).
10. **Module 10: Configuration Status Accounting (CSA)**
    - Real-time status accounting ledger tracking all CIs, versions, owners, lifecycle states, and baseline states.
    - Filtering by category, status, and owner with instant CSV export.
11. **Module 11: Baselines and Release Management**
    - Freezing authorized configuration baselines (`BL-001`, `BL-002`) containing approved CI versions only.
    - Software release bundling (`REL-001`, `REL-002`) mapped to baselines and tested CRs.
12. **Module 12: Configuration Verification and Auditing (FCA & PCA)**
    - **Functional Configuration Audit (FCA):** 6-item checklist verifying change implementation, traceability to tests, and defect resolution.
    - **Physical Configuration Audit (PCA):** 7-item checklist verifying source code tree hash, build artifacts, schema scripts, and documentation.
    - Dynamic status computation: `Passed`, `Conditional`, or `Failed`.
13. **Module 13: SCM Tool Integration (Git & GitHub)**
    - Feature 1: Git Version Control inspection and commit logging.
    - Feature 2: GitHub Issues representation and change request mapping.
    - Feature 3: GitHub Pull Request review workflow integration.
    - Feature 4: Automated CI/CD test workflow (`.github/workflows/tests.yml`).
14. **Module 14: SCM Standards and Process Improvement**
    - Academic cross-reference mapping framework features to SWEBOK v3.0, CMMI-DEV v2.0, ITIL v4, and ISO/IEC/IEEE 12207.
15. **Module 15: Reports & CSV Export Center**
    - 9 dedicated reports: *Status Accounting*, *Configuration Items*, *Version History*, *Change Requests*, *Trust Evaluations*, *Organizational Memory*, *FCA Audits*, *PCA Audits*, and *Baselines & Releases*.
    - One-click CSV downloads for every report.

---

## 5. Adaptive Trust Scoring Mathematical Formula

The trust score $\mathcal{T} \in [0, 100]$ estimates the reliability of a proposed configuration change based on empirical evidence:

$$\mathcal{T} = \operatorname{clamp}\left( \left( \mathcal{B}_{\text{cat}} \cdot \frac{W_{\text{base}}}{100} \right) + \left( \mathcal{M}_{\text{hist}} \cdot \frac{W_{\text{mem}}}{100} \right) + \mathcal{A}_{\text{author}} - \mathcal{P}_{\text{risk}} + \mathcal{R}_{\text{ready}} + 15.0,\; 5.0,\; 98.0 \right)$$

Where:
* $\mathcal{B}_{\text{cat}}$: Intrinsic stability rating of the CI category (e.g., Requirement Documents = 85, Configuration Files = 72, Deployment Scripts = 65).
* $W_{\text{base}}$: Configured category weight (default: 20%).
* $\mathcal{M}_{\text{hist}}$: Weighted historical outcome score derived from similar precedents in Organizational Memory:
  $$\mathcal{M}_{\text{hist}} = \frac{\sum_{i=1}^k \text{sim}_i \cdot \text{OutcomeScore}_i}{\sum_{i=1}^k \text{sim}_i}$$
  where $\text{Success} = 100$, $\text{Rollback} = 30$, $\text{Failure} = 10$.
* $W_{\text{mem}}$: Configured organizational memory weight (default: 45%).
* $\mathcal{A}_{\text{author}}$: Requester track record bonus ($+5.0$ if historical approval rate $\ge 75\%$, $-4.0$ if $< 40\%$).
* $\mathcal{P}_{\text{risk}}$: Risk level penalty (Low = 0, Medium = 6, High = 14, Critical = 22; $+4.0$ if business impact is High/Critical).
* $\mathcal{R}_{\text{ready}}$: Verification readiness bonus ($+4.0$ if diff and clear justification are supplied).

### Evidence Confidence Rating
* **High Confidence:** $\ge 3$ similar precedents matched with average similarity $\ge 45\%$.
* **Medium Confidence:** $1 - 2$ similar precedents matched.
* **Low Confidence:** No similar precedents found in memory.

### Action Recommendation Thresholds
* **Trust Score $\ge 80.0$:** High Trust &rarr; Recommend Approval Review by CCB.
* **Trust Score $60.0 - 79.9$:** Moderate Trust &rarr; Recommend Additional Validation (Regression / Staging tests).
* **Trust Score $< 60.0$:** Low Trust &rarr; Recommend Modification or Rejection Review.

---

## 6. Primary Demonstration Scenario

* **Change Request:** `CR-001`
* **Title:** CONFIGURATION TRUST THRESHOLD CHANGE
* **Target CI:** `CI-006` (Trust Evaluation Configuration)
* **Current Value:** `trust_threshold = 70`
* **Proposed Value:** `trust_threshold = 80`
* **System Execution:**
  1. Retrieves 3 similar threshold modifications from Organizational Memory (`MEM-001`, `MEM-002`, `MEM-003`).
  2. Analyzes outcomes: conservative increments to 70 and 75 succeeded with zero defects, whereas an extreme jump to 95 failed.
  3. Computes Trust Score: **84.0/100** (Evidence Confidence: **Medium**).
  4. Generates explainability breakdown citing positive precedent drivers.
  5. CCB reviewer approves change.
  6. Developer implements change &rarr; creates version `1.1` on `CI-006`.
  7. QA Engineer records passing verification test (35 passed, 0 failed).
  8. Change is closed and archived into Organizational Memory as new precedent.

---

## 7. Demo User Accounts

All demo accounts use the standard password: **`password123`**

| Role | Username | Password | Key Permissions |
| :--- | :--- | :--- | :--- |
| **Project Manager** | `pm_user` | `password123` | Full governance, CCB rulings, release authorization |
| **Configuration Manager**| `cm_user` | `password123` | CI cataloging, baselines, versioning, audit |
| **Developer** | `dev_user` | `password123` | Propose CRs, implement approved changes |
| **QA Engineer** | `qa_user` | `password123` | Record test results, conduct FCA/PCA audits |
| **DevOps Engineer** | `devops_user` | `password123` | Build scripts, deployment manifests, releases |
| **ML/Trust Analyst** | `analyst_user`| `password123` | Trust engine tuning, memory management |

### Student Team Accounts
* `yogalakshmi` (Project Manager Lead) - `password123`
* `pavithra` (Configuration Manager Lead) - `password123`
* `yuvaraj` (Developer & Trust Engineer) - `password123`

---

## 8. Installation & Windows Startup Instructions

### Quick Start (Recommended on Windows)
Simply double-click:
```cmd
run.bat
```
The script will automatically:
1. Verify Python 3.10+ installation.
2. Create and activate a virtual environment (`venv`).
3. Install dependencies from `requirements.txt`.
4. Initialize and seed SQLite database `scm_framework.db`.
5. Launch the Flask development server at `http://127.0.0.1:5000`.

### Manual Startup via PowerShell
```powershell
# 1. Navigate to project directory
cd f:\Explainable_SCM_Framework

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install required packages
pip install -r requirements.txt

# 4. Initialize and seed database
python init_db.py

# 5. Start the web application
python app.py
```
Open your browser at: **`http://127.0.0.1:5000`**

---

## 9. Automated Testing

Run the test suite using pytest:
```powershell
pytest -v
```
**Test Results:**
```text
============================= test session starts =============================
collected 22 items

tests/test_audits.py::test_fca_audit_calculation_passed_vs_failed PASSED [  4%]
tests/test_audits.py::test_audit_session_creation PASSED                 [  9%]
tests/test_audits.py::test_report_generation_and_csv_export PASSED       [ 13%]
tests/test_auth.py::test_app_startup_and_login_page PASSED               [ 18%]
tests/test_auth.py::test_database_initialization_users PASSED            [ 22%]
tests/test_auth.py::test_user_authentication_success PASSED              [ 27%]
tests/test_auth.py::test_user_authentication_failure PASSED              [ 31%]
tests/test_auth.py::test_quick_login_switcher PASSED                     [ 36%]
tests/test_auth.py::test_unauthorized_action_restriction PASSED          [ 40%]
tests/test_change_requests.py::test_change_request_creation PASSED       [ 45%]
tests/test_change_requests.py::test_invalid_transition_prevention PASSED [ 50%]
tests/test_change_requests.py::test_ccb_review_transition PASSED         [ 54%]
tests/test_configuration.py::test_configuration_item_creation PASSED     [ 59%]
tests/test_configuration.py::test_duplicate_ci_id_prevention PASSED      [ 63%]
tests/test_configuration.py::test_version_progression_and_diff PASSED    [ 68%]
tests/test_configuration.py::test_configuration_dependencies_traceability PASSED [ 72%]
tests/test_trust_engine.py::test_trust_score_calculation_bounds_and_validity PASSED [ 77%]
tests/test_trust_engine.py::test_similarity_retrieval_algorithm PASSED   [ 81%]
tests/test_trust_engine.py::test_explainability_diagnostic_output PASSED [ 86%]
tests/test_trust_engine.py::test_adaptive_model_tuning PASSED            [ 90%]
tests/test_workflow.py::test_complete_demonstration_scenario_lifecycle PASSED [ 95%]
tests/test_workflow.py::test_baseline_and_release_creation PASSED        [100%]

============================= 22 passed in 27.85s =============================
```

---

## 10. Screenshot Files

All 22 real screenshots are captured and located in the `screenshots/` directory:
* See [SCREENSHOT_GUIDE.md](file:///f:/Explainable_SCM_Framework/SCREENSHOT_GUIDE.md) for the complete Review 3 presentation walkthrough.

---

## 11. Known Limitations & Future Enhancements

* **Academic Prototype:** This framework is designed for local demonstration and academic project reviews; deploying to production would require Gunicorn/Waitress and PostgreSQL/MySQL instead of SQLite.
* **Remote Git Sync:** Remote GitHub synchronization requires a user-supplied GitHub Personal Access Token configured in the Settings module.
* **Future Work:** Integration with deep-learning based code semantic embedding models (e.g. CodeBERT) for multi-language AST-level change similarity estimation.
