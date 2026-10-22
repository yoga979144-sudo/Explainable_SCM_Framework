import os
import sys
import time
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from app import create_app

BASE_DIR = Path(__file__).resolve().parent
SCREENSHOT_DIR = BASE_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

PAGES_TO_CAPTURE = [
    ("01_login_page.png", "/login", False),
    ("02_dashboard.png", "/dashboard", True),
    ("03_configuration_items.png", "/configuration-items", True),
    ("04_configuration_detail.png", "/configuration-items/CI-006", True),
    ("05_traceability_matrix.png", "/traceability", True),
    ("06_version_history.png", "/version-history", True),
    ("07_version_comparator.png", "/version-compare?ci_id=CI-001&v1=1.0&v2=2.0", True),
    ("08_change_requests.png", "/change-requests", True),
    ("09_change_detail_review.png", "/change-requests/CR-001", True),
    ("10_organizational_memory.png", "/organizational-memory", True),
    ("11_similarity_retrieval.png", "/organizational-memory/similarity-test", True),
    ("12_trust_evaluation_engine.png", "/trust-evaluation", True),
    ("13_explainability_panel.png", "/explainability/CR-001", True),
    ("14_ccb_review_queue.png", "/ccb-review", True),
    ("15_status_accounting.png", "/status-accounting", True),
    ("16_baselines_management.png", "/baselines", True),
    ("17_releases_management.png", "/releases", True),
    ("18_fca_audit.png", "/fca-audit", True),
    ("19_pca_audit.png", "/pca-audit", True),
    ("20_github_integration.png", "/github-integration", True),
    ("21_scm_standards.png", "/scm-standards", True),
    ("22_reports_export.png", "/reports", True)
]

def run_flask_app():
    app = create_app('development')
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def get_webdriver():
    # Try Edge first
    try:
        edge_options = EdgeOptions()
        edge_options.add_argument("--headless=new")
        edge_options.add_argument("--window-size=1400,920")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--log-level=3")
        driver = webdriver.Edge(options=edge_options)
        return driver
    except Exception as e:
        print(f"Edge driver initialization notice: {e}. Trying Chrome...")
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1400,920")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")
        return webdriver.Chrome(options=chrome_options)

def capture_all():
    # Start Flask server in background thread
    server_thread = threading.Thread(target=run_flask_app, daemon=True)
    server_thread.start()
    time.sleep(2.5)  # Allow Flask server to initialize

    driver = get_webdriver()
    print("Browser driver launched successfully.")

    try:
        base_url = "http://127.0.0.1:5000"

        # Capture login page first (unauthenticated)
        driver.get(f"{base_url}/login")
        time.sleep(1.0)
        driver.save_screenshot(str(SCREENSHOT_DIR / "01_login_page.png"))
        print("Captured: 01_login_page.png")

        # Authenticate via quick-login
        driver.get(f"{base_url}/quick-login/pm_user")
        time.sleep(1.0)

        # Capture remaining authenticated pages
        for filename, route, needs_auth in PAGES_TO_CAPTURE:
            if filename == "01_login_page.png":
                continue
            url = f"{base_url}{route}"
            driver.get(url)
            time.sleep(1.2)  # Allow Chart.js animations to complete
            dest_path = str(SCREENSHOT_DIR / filename)
            driver.save_screenshot(dest_path)
            print(f"Captured: {filename}")

        print("\nALL 22 SCREENSHOTS CAPTURED SUCCESSFULLY IN screenshots/ DIRECTORY!")
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_all()
