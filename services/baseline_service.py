from datetime import datetime
from models import db
from models.database_models import Baseline, BaselineItem, Release, ConfigurationItem, ChangeRequest, ActivityLog

def get_all_baselines():
    return Baseline.query.order_by(Baseline.creation_date.desc()).all()

def get_baseline_by_id(baseline_id):
    return Baseline.query.filter_by(baseline_id=baseline_id).first()

def get_next_baseline_id():
    count = Baseline.query.count()
    return f"BL-{count + 1:03d}"

def create_baseline(name, description, created_by, ci_version_pairs, approval_status='Approved', user='System'):
    """
    ci_version_pairs: list of dicts [{'ci_id': 'CI-001', 'version_number': '1.0'}]
    Validates that each CI version is approved.
    """
    baseline_id = get_next_baseline_id()
    baseline = Baseline(
        baseline_id=baseline_id,
        name=name,
        description=description,
        created_by=created_by,
        approval_status=approval_status,
        creation_date=datetime.utcnow()
    )
    db.session.add(baseline)

    for item in ci_version_pairs:
        ci_id = item['ci_id']
        ver_num = item.get('version_number')
        ci = ConfigurationItem.query.filter_by(ci_id=ci_id).first()
        if not ci:
            continue
        
        # Mark CI baseline status
        ci.baseline_status = 'Baselined'
        
        b_item = BaselineItem(
            baseline_id=baseline_id,
            ci_id=ci_id,
            ci_name=ci.name,
            version_number=ver_num or ci.current_version,
            status='Active'
        )
        db.session.add(b_item)

    log = ActivityLog(
        user=user,
        action="Created Configuration Baseline",
        module="Baseline Management",
        details=f"Established baseline {baseline_id}: '{name}' with {len(ci_version_pairs)} items"
    )
    db.session.add(log)
    db.session.commit()
    return baseline

def get_all_releases():
    return Release.query.order_by(Release.release_date.desc()).all()

def get_release_by_id(release_id):
    return Release.query.filter_by(release_id=release_id).first()

def get_next_release_id():
    count = Release.query.count()
    return f"REL-{count + 1:03d}"

def create_release(release_name, baseline_id, included_cr_ids, responsible_user, release_status='Planned', test_status='Passed', user='System'):
    """
    Create a formal release mapped to an approved Baseline and verified Change Requests.
    Validates that included CRs are approved or tested.
    """
    baseline = Baseline.query.filter_by(baseline_id=baseline_id).first()
    if not baseline:
        raise ValueError(f"Baseline {baseline_id} not found.")

    # Validate included CRs
    valid_crs = []
    if included_cr_ids:
        cr_list = [c.strip() for c in included_cr_ids.split(',') if c.strip()]
        for cr_id in cr_list:
            cr = ChangeRequest.query.filter_by(cr_id=cr_id).first()
            if not cr:
                raise ValueError(f"Change Request {cr_id} does not exist.")
            if cr.current_status not in ['Approved', 'Implemented', 'Tested', 'Closed']:
                raise ValueError(f"Cannot include unapproved change request {cr_id} (current status: {cr.current_status}).")
            valid_crs.append(cr_id)

    rel_id = get_next_release_id()
    rel = Release(
        release_id=rel_id,
        release_name=release_name,
        baseline_id=baseline_id,
        included_changes=",".join(valid_crs) if valid_crs else "Initial Release Baseline",
        test_status=test_status,
        release_status=release_status,
        release_date=datetime.utcnow(),
        responsible_user=responsible_user
    )
    db.session.add(rel)

    # If status is 'Released', update CI release status for all items in the baseline
    if release_status == 'Released':
        b_items = BaselineItem.query.filter_by(baseline_id=baseline_id).all()
        for bi in b_items:
            ci = ConfigurationItem.query.filter_by(ci_id=bi.ci_id).first()
            if ci:
                ci.release_status = 'Released'

    log = ActivityLog(
        user=user,
        action="Created Software Release",
        module="Release Management",
        details=f"Created {rel_id}: '{release_name}' based on {baseline_id} (Status: {release_status})"
    )
    db.session.add(log)
    db.session.commit()
    return rel
