import difflib
import subprocess
from datetime import datetime
from models import db
from models.database_models import ConfigurationItem, ConfigurationVersion, ActivityLog

def get_versions_for_ci(ci_id):
    return ConfigurationVersion.query.filter_by(ci_id=ci_id).order_by(ConfigurationVersion.timestamp.desc()).all()

def get_all_versions():
    return ConfigurationVersion.query.order_by(ConfigurationVersion.timestamp.desc()).all()

def get_version_by_id(version_id):
    return ConfigurationVersion.query.filter_by(version_id=version_id).first()

def create_new_version(ci_id, new_version_number, change_description, author, configuration_content, approval_status='Approved', user='System'):
    ci = ConfigurationItem.query.filter_by(ci_id=ci_id).first()
    if not ci:
        raise ValueError(f"Configuration item {ci_id} not found.")

    prev_version = ci.current_version
    version_id = f"VER-{ci_id}-{new_version_number}"
    
    # Check if duplicate version exists
    existing = ConfigurationVersion.query.filter_by(version_id=version_id).first()
    if existing:
        raise ValueError(f"Version {version_id} already exists.")
    
    # Fetch previous version content for diff
    prev_ver_obj = ConfigurationVersion.query.filter_by(ci_id=ci_id, version_number=prev_version).first()
    prev_content = prev_ver_obj.configuration_content if prev_ver_obj else ""
    
    diff_lines = list(difflib.unified_diff(
        prev_content.splitlines(keepends=True),
        configuration_content.splitlines(keepends=True),
        fromfile=f"{ci_id} (v{prev_version})",
        tofile=f"{ci_id} (v{new_version_number})"
    ))
    diff_summary = "".join(diff_lines) if diff_lines else "No textual differences detected."

    ver = ConfigurationVersion(
        version_id=version_id,
        ci_id=ci_id,
        version_number=new_version_number,
        change_description=change_description,
        author=author,
        previous_version=prev_version,
        current_version=new_version_number,
        approval_status=approval_status,
        configuration_content=configuration_content,
        diff_summary=diff_summary
    )
    db.session.add(ver)

    # Update current version in ConfigurationItem
    ci.current_version = new_version_number
    ci.last_modified_date = datetime.utcnow()

    log = ActivityLog(
        user=user,
        action="Created Configuration Version",
        module="Version Control",
        details=f"Updated {ci_id} from v{prev_version} to v{new_version_number}: {change_description}"
    )
    db.session.add(log)
    db.session.commit()
    return ver

def compare_versions(ci_id, v1_number, v2_number):
    v1 = ConfigurationVersion.query.filter_by(ci_id=ci_id, version_number=v1_number).first()
    v2 = ConfigurationVersion.query.filter_by(ci_id=ci_id, version_number=v2_number).first()
    
    if not v1 or not v2:
        return {
            'error': f"Could not find versions {v1_number} and/or {v2_number} for {ci_id}."
        }
    
    content1 = (v1.configuration_content or "").splitlines()
    content2 = (v2.configuration_content or "").splitlines()
    
    differ = difflib.HtmlDiff(wrapcolumn=80)
    html_diff = differ.make_table(
        content1, 
        content2, 
        fromdesc=f"Version {v1.version_number} ({v1.author})", 
        todesc=f"Version {v2.version_number} ({v2.author})",
        context=True,
        numlines=3
    )

    raw_diff = list(difflib.unified_diff(
        (v1.configuration_content or "").splitlines(keepends=True),
        (v2.configuration_content or "").splitlines(keepends=True),
        fromfile=f"v{v1_number}",
        tofile=f"v{v2_number}"
    ))

    return {
        'v1': v1,
        'v2': v2,
        'html_diff': html_diff,
        'raw_diff': "".join(raw_diff) if raw_diff else "Identical content."
    }

def check_local_git_status():
    """Safely check if Git is installed and check local repo commits."""
    try:
        git_version_out = subprocess.run(
            ['git', '--version'], 
            capture_output=True, 
            text=True, 
            timeout=3
        )
        if git_version_out.returncode != 0:
            return {
                'installed': False,
                'message': 'Git executable is not available on system PATH.'
            }
        
        git_version = git_version_out.stdout.strip()

        # Check commit history in current workspace
        git_log = subprocess.run(
            ['git', 'log', '-n', '10', '--pretty=format:%h|%an|%ad|%s', '--date=short'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        commits = []
        if git_log.returncode == 0 and git_log.stdout.strip():
            for line in git_log.stdout.strip().split('\n'):
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'date': parts[2],
                        'message': parts[3]
                    })
        
        return {
            'installed': True,
            'git_version': git_version,
            'is_repo': git_log.returncode == 0,
            'commits': commits,
            'message': 'Git detected successfully.'
        }
    except FileNotFoundError:
        return {
            'installed': False,
            'message': 'Git command not found on Windows PATH. Application-level configuration history is active.'
        }
    except Exception as e:
        return {
            'installed': False,
            'message': f'Git check encountered: {str(e)}'
        }
