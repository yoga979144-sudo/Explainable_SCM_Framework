# Review 3 Git and GitHub SCM Demonstration Guide

**Project Title:** Explainable Organizational Memory-Driven SCM Framework Using Adaptive Configuration Trust Learning  
**Target Milestone:** Academic Project Review 3  
**Authors:**
* **YOGALAKSHMI S** (23MIS0383)
* **PAVITHRA L** (23MIS0160)
* **YUVARAJ G** (24MIS0403)

---

## Welcome to Your Review 3 Guide!

This guide is written in clear, simple English so you can confidently explain and demonstrate your Software Configuration Management (SCM) project to your professor or project review committee.

Everything described here has been **actually built, tested, and verified** in your project folder `F:\Explainable_SCM_Framework`.

---

## 1. How Git and GitHub Features Connect to SCM Concepts

In your viva or project presentation, your professor will want to know how native Git/GitHub features connect to formal SCM knowledge areas (such as IEEE/SWEBOK and ISO 12207):

| SCM Concept | What it Means in SCM Theory | How Implemented via Git / GitHub | How Implemented in Your Web Application |
| :--- | :--- | :--- | :--- |
| **Version Management** | Tracking modifications over time without overwriting previous history. | **Git Commits:** Every commit creates a cryptographic SHA-1/SHA-256 hash snapshot of project files. | **Version Service:** Application records version history in SQLite and provides a side-by-side colorized diff comparator. |
| **Branch Management** | Allowing multiple developers to work on features in parallel without breaking the main codebase. | **Git Branches:** `main`, `feature/version-management`, `feature/change-management`, `feature/problem-tracking`, `feature/trust-learning`. | **Traceability Matrix:** Tracks which configuration items and change requests relate to each branch. |
| **Change Management** | Evaluating and approving change requests before they reach production. | **GitHub Pull Requests:** Proposing changes, code review, diff inspection, and discussion. | **CCB Review Module:** Human-in-the-loop review board where Project Managers approve/reject CRs. |
| **Problem Tracking** | Recording defects or anomalies and tracking them through to resolution. | **GitHub Issues:** Creating tickets for bugs, enhancements, and tasks. | **Change Requests (CRs):** Categorized by risk (Low/Med/High/Critical) with immutable transition audit trails. |
| **Baseline & Promotion Management** | Freezing an approved set of artifacts and moving them toward release. | **Git Tags:** Annotated tags `v1.0.0` and `v1.1.0` freezing exact commit snapshots. | **Baselines Module:** Locking approved CI versions into baselines (`BL-001`, `BL-002`). |
| **Release Management** | Formally publishing packaged, audited software to stakeholders. | **GitHub Releases:** Associating tags with markdown release notes and downloadable source bundles. | **Releases Module:** Generating release records (`REL-001`, `REL-002`) mapped to approved baselines. |
| **System Building & CI/CD** | Automatically compiling and verifying work products against test suites. | **GitHub Actions:** `.github/workflows/tests.yml` running Pytest automatically on every push. | **Automated Test Suite:** 22/22 Pytest verification tests with 100% pass rate. |
| **Status Accounting** | Recording and reporting the status of every configuration item. | **Git Log & GitHub Insights:** Commit graphs, branch network, and commit history. | **Status Accounting (CSA):** Filterable ledger tracking CI states with one-click CSV export. |
| **Configuration Audits** | Verifying functional completeness and physical baseline matching. | **Git Diff & Tag Inspection:** Comparing release tags against baselines. | **FCA / PCA Audits:** 6-item Functional and 7-item Physical audit checklists calculating status dynamically. |
| **Organizational Memory & Trust (Novel)** | Storing past change outcomes and predicting the reliability of proposed drifts. | *Custom Novel Contribution* (Git does not do this natively). | **Adaptive Trust Engine:** Scikit-learn TF-IDF cosine similarity matching against 8 historical memory records to score trust (0-100). |

---

## 2. Step-by-Step Viva Demonstration Script (Follow This During Review)

Follow these 7 steps during your presentation. You can show the terminal commands and the web application side by side.

### Step 1: Prove Git Repository and Clean Working Tree
**What to say to your professor:**
> *"Sir, we have initialized our project as a formal Git repository on branch `main`. We configured `.gitignore` to strictly exclude virtual environments, SQLite database files, and caches to preserve repository integrity."*

**Commands to run in terminal:**
```bash
git status
```
**Expected output:**
```text
On branch main
nothing to commit, working tree clean
```
**Evidence:** [EVIDENCE_CHECKLIST.md](file:///f:/Explainable_SCM_Framework/docs/implementation/EVIDENCE_CHECKLIST.md) (EV-01)

---

### Step 2: Demonstrate Parallel Development with Feature Branches
**What to say to your professor:**
> *"Sir, to demonstrate parallel development, we have created 4 dedicated feature branches alongside `main`: `feature/version-management`, `feature/change-management`, `feature/problem-tracking`, and `feature/trust-learning`. Each branch represents a specific SCM capability with distinct commits."*

**Commands to run in terminal:**
```bash
git branch -v
```
**Expected output:**
```text
  feature/change-management  af51f60 docs(change): specify CCB state transition pipeline and gate criteria
  feature/problem-tracking   620988d docs(problem): establish defect logging and incident-to-CR traceability rules
  feature/trust-learning     525e538 feat(trust): update trust threshold from 70 to 80 based on empirical memory precedent (CR-001)
  feature/version-management 96f20ef docs(version): define SCM version progression and verification gate rules
* main                       101d450 merge(trust): integrate adaptive trust threshold update (CR-001)
```
**Evidence:** [EVIDENCE_CHECKLIST.md](file:///f:/Explainable_SCM_Framework/docs/implementation/EVIDENCE_CHECKLIST.md) (EV-05)

---

### Step 3: Demonstrate Version Changes (The Core Academic Scenario)
**What to say to your professor:**
> *"Sir, for our core demonstration scenario, we proposed a configuration change (CR-001) to update the trust threshold from 70 to 80 in `config/trust_engine_params.json`. We committed this modification on `feature/trust-learning`, inspected the diff, and verified it against baseline Version 1.0."*

**Commands to run in terminal:**
```bash
# 1. Show the original version recorded at tag v1.0.0
git show v1.0.0:config/trust_engine_params.json

# 2. Show the difference between v1.0.0 (threshold 70) and v1.1.0 (threshold 80)
git diff v1.0.0 v1.1.0
```
**Expected diff output:**
```diff
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
**Evidence:** [`screenshots/07_version_comparator.png`](file:///f:/Explainable_SCM_Framework/screenshots/07_version_comparator.png)

---

### Step 4: Demonstrate Branch Merging & Commit Topology
**What to say to your professor:**
> *"Sir, after CCB review approval and QA testing, we merged `feature/trust-learning` into `main` using a non-fast-forward merge (`--no-ff`) to preserve branch history and traceability. Here is the visual commit graph."*

**Commands to run in terminal:**
```bash
git log --graph --oneline -5
```
**Expected output:**
```text
*   101d450 merge(trust): integrate adaptive trust threshold update (CR-001)
|\  
| * 525e538 feat(trust): update trust threshold from 70 to 80 based on empirical memory precedent (CR-001)
|/  
* 631f194 feat(config): establish baseline trust engine parameters v1.0 with threshold 70
* 371313b feat(scm): initial baseline release for Explainable SCM Framework
```
**Evidence:** [EVIDENCE_CHECKLIST.md](file:///f:/Explainable_SCM_Framework/docs/implementation/EVIDENCE_CHECKLIST.md) (EV-20)

---

### Step 5: Demonstrate Version Tagging & Releases
**What to say to your professor:**
> *"Sir, we used annotated Git tags to identify frozen release baselines: `v1.0.0` for the initial system foundation, and `v1.1.0` for the approved threshold optimization. Annotated tags record the tagger, date, message, and target commit."*

**Commands to run in terminal:**
```bash
git tag -l -n
git show v1.0.0 --stat
```
**Evidence:** [`docs/RELEASE_NOTES_v1.0.0.md`](file:///f:/Explainable_SCM_Framework/docs/RELEASE_NOTES_v1.0.0.md) & [`docs/RELEASE_NOTES_v1.1.0.md`](file:///f:/Explainable_SCM_Framework/docs/RELEASE_NOTES_v1.1.0.md)

---

### Step 6: Demonstrate the Running Web Application
**What to say to your professor:**
> *"Sir, now let us look at the live application running on `http://127.0.0.1:5000`. We have captured real screenshots of all 22 views in the `screenshots/` directory."*

Point out the following key views:
1. **Dashboard (`02_dashboard.png`):** Show the real-time counters (12 CIs, 8 memory items) and Chart.js charts.
2. **Explainability Panel (`13_explainability_panel.png`):** Show CR-001's trust score (**84.0/100**), confidence (**Medium**), positive drivers, risk deductions, and the 3 cited precedents from Organizational Memory.
3. **CCB Review Queue (`14_ccb_review_queue.png`):** Show formal Change Control Board governance rulings.
4. **Status Accounting (`15_status_accounting.png`):** Show the live status ledger with CSV download.
5. **Configuration Audits (`18_fca_audit.png` & `19_pca_audit.png`):** Show the 6-question FCA and 7-question PCA checklists.
6. **GitHub SCM Integration (`20_github_integration.png`):** Show the 4-feature integration matrix and issue mappings.

---

### Step 7: Demonstrate Automated Test Suite
**What to say to your professor:**
> *"Sir, our project includes a comprehensive automated test suite with 22 Pytest assertions. All tests execute with a 100% pass rate in under 30 seconds."*

**Command to run:**
```bash
pytest -v
```
**Expected output:**
```text
============================= 22 passed in 26.73s =============================
```

---

## 3. How to Connect Your Local Project to a Remote GitHub Repository

If you want to push this project to your GitHub account (e.g. `github.com/yogalakshmi-vit/Explainable-SCM-Framework`):

### Step A: Create a New Repository on GitHub
1. Open your web browser and go to: `https://github.com/new`.
2. Repository name: `Explainable-SCM-Framework`
3. Description: `Explainable Organizational Memory-Driven SCM Framework Using Adaptive Configuration Trust Learning`
4. Choose **Public** (or **Private**).
5. **IMPORTANT:** Do NOT initialize with a README, .gitignore, or license (we already have them!).
6. Click **Create repository**.

### Step B: Add the Remote and Push
Open PowerShell in `F:\Explainable_SCM_Framework` and run:
```bash
# 1. Add your GitHub remote (replace with your actual GitHub username)
git remote add origin https://github.com/<your-github-username>/Explainable-SCM-Framework.git

# 2. Rename branch to main (already main, but safe to verify)
git branch -M main

# 3. Push the main branch
git push -u origin main

# 4. Push all feature branches
git push origin feature/version-management
git push origin feature/change-management
git push origin feature/problem-tracking
git push origin feature/trust-learning

# 5. Push all tags (v1.0.0 and v1.1.0)
git push origin --tags
```

### Step C: Publish GitHub Release on GitHub Website
1. Go to your repository on GitHub.
2. In the right sidebar, click **Releases** &rarr; **Draft a new release**.
3. Select tag `v1.0.0`.
4. Title: `SCM Framework v1.0.0`.
5. Paste the text from [`docs/RELEASE_NOTES_v1.0.0.md`](file:///f:/Explainable_SCM_Framework/docs/RELEASE_NOTES_v1.0.0.md).
6. Click **Publish release**!

---

## 4. What Has Been Implemented vs What Remains

### Implemented & Verified in Your Project:
* [x] Git local repository initialization on `main` branch.
* [x] Comprehensive `.gitignore` protecting secrets, databases, caches, and virtual environments.
* [x] 4 dedicated feature branches (`feature/version-management`, `feature/change-management`, `feature/problem-tracking`, `feature/trust-learning`).
* [x] Real configuration change demonstration (`trust_threshold = 70` &rarr; `80`) on `feature/trust-learning`.
* [x] Safe non-fast-forward merge into `main` with preserved branch topology.
* [x] Annotated version tags `v1.0.0` and `v1.1.0` with version diffing.
* [x] Complete release notes for both `v1.0.0` and `v1.1.0`.
* [x] Review 3 SCM Tool Integration Hub page (`github_integration.html`).
* [x] GitHub Actions automated CI workflow (`.github/workflows/tests.yml`).
* [x] 22 real PNG screenshots captured from live application in `screenshots/`.
* [x] 22 automated Pytest test cases passing 100%.

### Remaining Optional Steps (Requires Internet & GitHub Account):
* [ ] Creating the remote repository on `github.com` and running `git push -u origin main --tags`.
* [ ] Clicking "Publish Release" on the GitHub web UI using the release notes we prepared.
* [ ] Capturing the GitHub web browser screenshots once pushed.

---

## 5. Summary Table for Review 3 Checklist

| Item | Requirement | Status | Evidence |
| :---: | :--- | :---: | :--- |
| 1 | Git Installation | **Verified** | `git version 2.47.1.windows.1` |
| 2 | Local Repository | **Initialized** | Branch `main`, clean working tree |
| 3 | `.gitignore` | **Active** | Excludes `*.db`, `__pycache__`, `venv`, `.env` |
| 4 | Branches Created | **5 Branches** | `main` + 4 feature branches |
| 5 | Branch Merging | **Completed** | Merged `feature/trust-learning` into `main` |
| 6 | Version Diff | **Demonstrated** | `git diff v1.0.0 v1.1.0` (70 &rarr; 80) |
| 7 | Annotated Tags | **2 Tags** | `v1.0.0` & `v1.1.0` |
| 8 | Release Notes | **Prepared** | `RELEASE_NOTES_v1.0.0.md` & `v1.1.0.md` |
| 9 | GitHub Actions | **Configured** | `.github/workflows/tests.yml` |
| 10 | Application SCM | **Operational** | 15 modules running at `http://127.0.0.1:5000` |
| 11 | Automated Tests | **22 Passed** | 100% pass rate via Pytest |
| 12 | Evidence Files | **Available** | `screenshots/` (22 PNGs) & `docs/` |
