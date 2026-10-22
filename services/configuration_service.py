from models import db
from models.database_models import ConfigurationItem, ConfigurationVersion, ConfigurationDependency, ActivityLog
from datetime import datetime

CI_CATEGORIES = [
    "Source Code",
    "Requirement Documents",
    "Design Documents",
    "Test Cases",
    "Build Scripts",
    "Configuration Files",
    "Deployment Scripts",
    "Database Schemas",
    "Machine Learning Models",
    "Organizational Knowledge Repository"
]

CI_STATUSES = ["Draft", "In-Review", "Approved", "Baselined", "Released", "Deprecated"]

def get_all_cis(category=None, status=None, search=None):
    query = ConfigurationItem.query
    if category and category != 'All':
        query = query.filter(ConfigurationItem.category == category)
    if status and status != 'All':
        query = query.filter(ConfigurationItem.status == status)
    if search:
        term = f"%{search}%"
        query = query.filter(
            (ConfigurationItem.ci_id.ilike(term)) |
            (ConfigurationItem.name.ilike(term)) |
            (ConfigurationItem.owner.ilike(term)) |
            (ConfigurationItem.description.ilike(term))
        )
    return query.order_by(ConfigurationItem.ci_id.asc()).all()

def get_ci_by_id(ci_id):
    return ConfigurationItem.query.filter_by(ci_id=ci_id).first()

def get_next_ci_id():
    count = ConfigurationItem.query.count()
    return f"CI-{count + 1:03d}"

def create_ci(ci_id, name, category, description, owner, status='Draft', current_version='1.0', file_path=None, user='System'):
    if not ci_id:
        ci_id = get_next_ci_id()
    
    existing = ConfigurationItem.query.filter_by(ci_id=ci_id).first()
    if existing:
        raise ValueError(f"Configuration Item with ID {ci_id} already exists.")
    
    ci = ConfigurationItem(
        ci_id=ci_id,
        name=name,
        category=category,
        description=description,
        owner=owner,
        status=status,
        current_version=current_version,
        file_path=file_path,
        approval_status='Approved' if status in ['Approved', 'Baselined', 'Released'] else 'Pending',
        baseline_status='Baselined' if status == 'Baselined' else 'Unbaselined',
        release_status='Released' if status == 'Released' else 'Unreleased'
    )
    db.session.add(ci)
    
    # Create initial version record
    ver_id = f"VER-{ci_id}-{current_version}"
    ver = ConfigurationVersion(
        version_id=ver_id,
        ci_id=ci_id,
        version_number=current_version,
        change_description="Initial configuration baseline",
        author=owner,
        previous_version=None,
        current_version=current_version,
        approval_status=ci.approval_status,
        configuration_content=f"# Baseline Configuration for {name}\nversion: {current_version}\nstatus: active"
    )
    db.session.add(ver)

    # Activity log
    log = ActivityLog(
        user=user,
        action="Created Configuration Item",
        module="Configuration Identification",
        details=f"Created {ci_id}: {name} ({category}) at version {current_version}"
    )
    db.session.add(log)
    db.session.commit()
    return ci

def update_ci(ci_id, name=None, category=None, description=None, owner=None, status=None, user='System'):
    ci = get_ci_by_id(ci_id)
    if not ci:
        raise ValueError(f"Configuration Item {ci_id} not found.")
    
    changes = []
    if name and ci.name != name:
        changes.append(f"name: {ci.name} -> {name}")
        ci.name = name
    if category and ci.category != category:
        changes.append(f"category: {ci.category} -> {category}")
        ci.category = category
    if description is not None and ci.description != description:
        ci.description = description
    if owner and ci.owner != owner:
        changes.append(f"owner: {ci.owner} -> {owner}")
        ci.owner = owner
    if status and ci.status != status:
        changes.append(f"status: {ci.status} -> {status}")
        ci.status = status
        if status in ['Approved', 'Baselined', 'Released']:
            ci.approval_status = 'Approved'
        if status == 'Baselined':
            ci.baseline_status = 'Baselined'
        if status == 'Released':
            ci.release_status = 'Released'

    ci.last_modified_date = datetime.utcnow()
    
    log = ActivityLog(
        user=user,
        action="Updated Configuration Item",
        module="Configuration Identification",
        details=f"Updated {ci_id}: " + (", ".join(changes) if changes else "metadata updated")
    )
    db.session.add(log)
    db.session.commit()
    return ci

def add_dependency(source_ci_id, target_ci_id, dependency_type, description="", user='System'):
    dep = ConfigurationDependency(
        source_ci_id=source_ci_id,
        target_ci_id=target_ci_id,
        dependency_type=dependency_type,
        description=description
    )
    db.session.add(dep)
    
    log = ActivityLog(
        user=user,
        action="Added Dependency",
        module="Configuration Identification",
        details=f"Linked {source_ci_id} -> {target_ci_id} ({dependency_type})"
    )
    db.session.add(log)
    db.session.commit()
    return dep

def get_ci_dependencies(ci_id):
    outgoing = ConfigurationDependency.query.filter_by(source_ci_id=ci_id).all()
    incoming = ConfigurationDependency.query.filter_by(target_ci_id=ci_id).all()
    return {'outgoing': outgoing, 'incoming': incoming}

def get_traceability_graph():
    cis = ConfigurationItem.query.all()
    deps = ConfigurationDependency.query.all()
    
    nodes = []
    for ci in cis:
        nodes.append({
            'id': ci.ci_id,
            'label': f"{ci.ci_id}: {ci.name}",
            'category': ci.category,
            'version': ci.current_version,
            'status': ci.status
        })
    
    links = []
    for dep in deps:
        links.append({
            'source': dep.source_ci_id,
            'target': dep.target_ci_id,
            'type': dep.dependency_type
        })
    
    return {'nodes': nodes, 'links': links}
