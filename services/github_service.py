import os
import requests
from pathlib import Path
from models import db
from models.database_models import GitHubSetting, ActivityLog, ChangeRequest
from services.version_service import check_local_git_status

GITHUB_API_BASE = "https://api.github.com"

def get_github_settings():
    setting = GitHubSetting.query.first()
    if not setting:
        setting = GitHubSetting(
            repo_name=os.getenv("GITHUB_REPO", ""),
            api_token=os.getenv("GITHUB_TOKEN", ""),
            sync_issues=True,
            sync_pull_requests=True,
            status_message="Not configured. Running in internal application-level mode."
        )
        db.session.add(setting)
        db.session.commit()
    return setting

def update_github_settings(repo_name, api_token, user='System'):
    setting = get_github_settings()
    setting.repo_name = repo_name.strip() if repo_name else ""
    setting.api_token = api_token.strip() if api_token else ""
    
    # Test connection if credentials provided
    if setting.repo_name and setting.api_token:
        try:
            headers = {
                "Authorization": f"Bearer {setting.api_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Explainable-SCM-Framework"
            }
            res = requests.get(f"{GITHUB_API_BASE}/repos/{setting.repo_name}", headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                setting.status_message = f"Connected successfully to GitHub repository: {data.get('full_name')}"
            else:
                setting.status_message = f"Connection failed (HTTP {res.status_code}): {res.json().get('message', 'Check token or repository name')}"
        except Exception as e:
            setting.status_message = f"API connection error: {str(e)}"
    else:
        setting.status_message = "No remote GitHub credentials provided. Using internal simulation & application-level tracking."

    log = ActivityLog(
        user=user,
        action="Updated GitHub Settings",
        module="SCM Tool Integration",
        details=f"Repository: {setting.repo_name or 'None'}, Status: {setting.status_message}"
    )
    db.session.add(log)
    db.session.commit()
    return setting

def get_github_integration_overview():
    setting = get_github_settings()
    local_git = check_local_git_status()
    
    # Check if .github/workflows/tests.yml exists
    workflow_path = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "tests.yml"
    workflow_exists = workflow_path.exists()

    # Internal Issue mapping
    crs = ChangeRequest.query.all()
    mapped_issues = [
        {
            'internal_cr_id': cr.cr_id,
            'title': cr.title,
            'github_issue_number': f"#{cr.id}",
            'status': 'Open' if cr.current_status not in ['Closed', 'Rejected'] else 'Closed',
            'requester': cr.requester,
            'mapped_type': 'Internal SCM Change Request (GitHub Issue Representation)'
        }
        for cr in crs
    ]

    # Features implemented summary
    features = [
        {
            'feature': 'Feature 1: Git Version Control',
            'description': 'Maintains configuration items, captures version diffs, and inspects local Git installation and commit histories.',
            'status': 'Active (Local Git check: ' + ('Installed' if local_git['installed'] else 'Not Installed; App History Active') + ')',
            'requires_credentials': False
        },
        {
            'feature': 'Feature 2: GitHub Issues Integration',
            'description': 'Maps configuration change requests (CRs) to structured issue tracking with risk and impact classification.',
            'status': 'Active (Internal workflow); Remote sync: ' + ('Connected' if 'Connected' in setting.status_message else 'Optional Token Required'),
            'requires_credentials': True
        },
        {
            'feature': 'Feature 3: GitHub Pull Requests Review',
            'description': 'CCB review and approval interface mirroring Pull Request review with trust metrics, explanations, and diff inspection.',
            'status': 'Active (Internal CCB workflow); Remote PR sync: Optional Token Required',
            'requires_credentials': True
        },
        {
            'feature': 'Feature 4: GitHub Actions CI/CD',
            'description': 'Automated test suite configured via .github/workflows/tests.yml to execute pytest across Ubuntu and Windows runners.',
            'status': 'Configured and Ready (.github/workflows/tests.yml present)' if workflow_exists else 'Workflow file pending',
            'requires_credentials': False
        }
    ]

    return {
        'setting': setting,
        'local_git': local_git,
        'workflow_exists': workflow_exists,
        'features': features,
        'mapped_issues': mapped_issues
    }
