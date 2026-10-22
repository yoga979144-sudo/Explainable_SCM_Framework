# Release Notes: SCM Framework v1.0.0

## Release Title
**SCM Framework v1.0.0 — Initial Baseline Release**

* **Tag:** `v1.0.0`
* **Target Commit:** `631f1943b999bc3659c70328f0cafa6cd3c3ccfe`
* **Date:** October 2026
* **Academic Review Milestone:** Review 3

---

## 1. Summary of Implemented Features

This release establishes the authoritative initial baseline for the **Explainable Organizational Memory-Driven SCM Framework Using Adaptive Configuration Trust Learning**. It combines enterprise software configuration management activities with trustworthy artificial intelligence and empirical knowledge reuse.

Key capabilities included in this release:
1. **Multi-Role Authentication & Access Governance:**
   - 6 standard stakeholder roles (*Project Manager*, *Configuration Manager*, *Developer*, *QA Engineer*, *DevOps Engineer*, *ML/Trust Analyst*).
   - PBKDF2 password hashing with SHA-256 and role permission gate checking.
2. **Configuration Identification (CI Management):**
   - 12 initial Configuration Items cataloged across 10 IEEE categories (Source Code, Requirements, Architecture, Test Cases, Build Scripts, Schemas, etc.).
   - Multi-stage lifecycle traceability mapping SRS requirements &rarr; Source Code &rarr; Tests &rarr; Configurations &rarr; Release Bundles.
3. **Application-Level Version Control & Visual Comparator:**
   - Line-by-line unified differential inspection and side-by-side visual HTML diffing.
   - Independent application version ledger with author and timestamp tracking.
4. **Configuration Change Request (CR) Management:**
   - Proposal specification with risk assessment (Low, Medium, High, Critical) and business impact estimation.
   - Immutable audit trail tracking every transition from `Draft` to `Closed`.
5. **Organizational Memory Repository:**
   - Institutional memory seeded with 8 empirical configuration change records.
   - Semantic retrieval using scikit-learn TF-IDF vectorization and cosine alignment.
6. **Adaptive Configuration Trust Learning:**
   - Mathematical formula ($0 - 100$) evaluating change reliability using category stability baselines, historical precedents, and risk penalties.
   - Separation of Trust Score, Evidence Confidence, and Recommendations.
7. **Explainable AI (XAI) Diagnostics:**
   - Transparent decomposition into positive drivers, risk penalties, and cited memory precedents.
8. **Change Control Board (CCB) Review Workflow:**
   - Formal board review interface enforcing human-in-the-loop rulings (*Approve*, *Reject*, *Request Modification*).
9. **Configuration Status Accounting (CSA):**
   - Live ledger tracking lifecycle, approval, baseline, and release states with instant CSV export.
10. **Baselines & Release Management:**
    - Authorized configuration baselines (`BL-001`, `BL-002`) and release bundles (`REL-001`, `REL-002`).
11. **Configuration Audits (FCA & PCA):**
    - 6-item Functional Configuration Audit and 7-item Physical Configuration Audit checklist evaluation.
12. **Automated CI/CD Integration:**
    - GitHub Actions pipeline definition in `.github/workflows/tests.yml`.

---

## 2. Main Changes in this Version

* Initialized complete full-stack web application structure (Flask, SQLAlchemy, SQLite, Bootstrap 5.3, Chart.js).
* Configured baseline configuration parameters for CI-006 (`config/trust_engine_params.json`) with initial `trust_threshold = 70`.
* Seeded comprehensive academic demonstration dataset including Change Request `CR-001`.
* Formulated adaptive trust learning engine model `v1.0-adaptive-rules`.
* Authored 22 automated Pytest verification cases covering all functional modules.

---

## 3. Testing Status

* **Automated Test Suite:** 22 passing tests out of 22 (100% pass rate).
* **Execution Time:** ~26 seconds via pytest.
* **Coverage Scope:** Authentication, CI creation, version diffing, CR lifecycle, CCB transitions, trust bounds, TF-IDF cosine similarity, FCA/PCA calculations, status accounting, and CSV exports.

---

## 4. Known Limitations

* **Local Academic Scope:** Designed for local demonstration running on SQLite and Flask's WSGI development server.
* **Remote GitHub API Sync:** Live synchronization with GitHub Issues and Pull Requests requires a user-configured Personal Access Token in the Settings module.
* **Semantic Analysis:** Current similarity retrieval uses TF-IDF n-gram vectorization; deep AST-level transformer embeddings (e.g. CodeBERT) are reserved for future work.

---

## 5. Installation & Verification Instructions

### Step 1: Clone or Open Project
```bash
cd f:\Explainable_SCM_Framework
```

### Step 2: Launch via 1-Click Windows Batch Script
```cmd
run.bat
```
*Automatically provisions `venv`, installs `requirements.txt`, initializes `scm_framework.db`, and launches the application at `http://127.0.0.1:5000`.*

### Step 3: Run Automated Test Suite
```bash
pytest -v
```

---

## 6. How to Publish this Release on GitHub

1. Push the repository and tags to your GitHub remote:
   ```bash
   git push origin main
   git push origin --tags
   ```
2. Navigate to your repository on GitHub: `https://github.com/<your-username>/<your-repo>`.
3. In the right sidebar, click **Releases**, then click **Draft a new release**.
4. In the **Choose a tag** dropdown, select `v1.0.0`.
5. Set the **Release title** to: `SCM Framework v1.0.0`.
6. Copy and paste the contents of this file into the release description text area.
7. Click **Publish release**.
