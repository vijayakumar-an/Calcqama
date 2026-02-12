# tests/conftest.py
import json
from pathlib import Path

import pytest
import yaml

# Appium 3 helpers + AppSession shim from the drivers package
from libs.drivers.app_session import start_calculator, safe_quit, AppSession
from libs.flows.windows.calculator import CalculatorFlows

from libs.utils.logger import init_logger, get_logger

LOG = get_logger("conftest")


# ------------------------------------------------------------------
# Session-level setup
# ------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def _init_logging():
    """Initialize global logger for all tests."""
    try:
        # Make sure your logging dict in config/config.yaml contains: "version": 1
        init_logger("config/config.yaml")
        LOG.info("Logger initialized successfully")
    except Exception as e:
        # Do not break the test run if logging init fails
        print(f"Failed to initialize logger: {e}")


@pytest.fixture(scope="session")
def config():
    """Load main YAML configuration."""
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


@pytest.fixture(scope="session")
def artifacts_dir(config):
    """Create artifacts directory for screenshots and reports."""
    d = Path(config.get("run", {}).get("artifacts_dir", "artifacts"))
    d.mkdir(parents=True, exist_ok=True)
    return d


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
def _cfg_get(dct, path, default=None):
    """Get nested config value by dot-separated path."""
    cur = dct
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def _load_json_file(path: Path):
    """Load JSON file safely. Returns empty dict if missing."""
    if not path.exists():
        LOG.warning(f"JSON file not found: {path}")
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f) or {}


# ------------------------------------------------------------------
# Screenshot-on-failure hook (records test outcome on node)
# ------------------------------------------------------------------
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ------------------------------------------------------------------
# Calculator UI map
# ------------------------------------------------------------------
@pytest.fixture(scope="session")
def calculator_ui_map(config):
    """Load calculator UI map from module-specific path or default."""
    # Prefer module config, fallback to default path
    path_str = _cfg_get(config, "modules.calculator.resources.ui_map") or \
               str(Path("resources") / "ui_map" / "windows" / "calculator.json")

    # Resolve absolute path from repo root so it's robust regardless of CWD
    path = Path(path_str)
    if not path.is_absolute():
        # conftest.py typically sits under tests/; go up to repo root
        repo_root = Path(__file__).resolve().parents[1]
        path = (repo_root / path).resolve()

    data = _load_json_file(path)
    # Your flows expect flat keys like "num_1", "plus", "result", etc.
    # Some maps nest under "locators"; support both.
    return data.get("locators", data)


# ------------------------------------------------------------------
# Calculator driver (Appium 3)
# ------------------------------------------------------------------
@pytest.fixture(scope="function")
def calc_driver(config, artifacts_dir, request):
    """
    Starts/stops Calculator via Appium 3 Windows driver.
    """
    # Helpful diagnostics: log which server/app we’re about to use
    mod = config.get("modules", {}).get("calculator", {}) or {}
    app_cfg = mod.get("app", {}) or {}
    app_val = app_cfg.get("app") or app_cfg.get("app_id") or app_cfg.get("app_path")

    wa_global = config.get("winappdriver", {}) or {}
    wa_module = mod.get("winappdriver", {}) or {}
    server_url = wa_module.get("server_url") or wa_global.get("server_url") or "http://127.0.0.1:4723"

    LOG.info(f"[DriverInit] module=calculator, server_url={server_url}, app={app_val}")

    drv = None
    try:
        # Uses namespaced caps (appium:*) under Appium 3
        drv = start_calculator(config, retries=2, retry_wait_sec=1.0)
        yield drv
    except Exception as e:
        LOG.error(f"Failed to start Calculator driver: {e}")
        raise
    finally:
        # Screenshot on failure (best-effort even if driver already died)
        if config.get("run", {}).get("screenshots_on_failure", True):
            rep = getattr(request.node, "rep_call", None)
            if rep and rep.failed:
                png = artifacts_dir / f"{request.node.name}_calculator.png"
                try:
                    if drv:
                        drv.save_screenshot(str(png))
                        LOG.info(f"Saved failure screenshot: {png}")
                except Exception as e:
                    LOG.warning(f"Failed to take screenshot: {e}")

        # Quit driver safely
        safe_quit(drv)


# ------------------------------------------------------------------
# Calculator AppSession (flows expect this wrapper)
# ------------------------------------------------------------------
@pytest.fixture(scope="function")
def calc_app(calc_driver, calculator_ui_map):
    """
    Wrap the raw driver + ui_map in an AppSession, because CalculatorFlows
    expects a single session object exposing methods like:
      compute, press_number, press_operator, click_button, get_result_value, etc.
    """
    session = AppSession(calc_driver, calculator_ui_map)
    # Optional pre-test reset
    try:
        session.clear()
    except Exception:
        pass
    yield session
    # Optional post-test reset
    try:
        session.clear()
    except Exception:
        pass


# ------------------------------------------------------------------
# Calculator Flows
# ------------------------------------------------------------------
@pytest.fixture(scope="function")
def calc(calc_app):
    """High-level CalculatorFlows for test steps."""
    return CalculatorFlows(calc_app)




# for microsoft todo

@pytest.fixture(scope="function")
def todo_driver(config):
    from libs.drivers.app_session import start_app, safe_quit

    drv = None
    try:
        drv = start_app(config, "microsoft_todo")
        yield drv
    finally:
        safe_quit(drv)


@pytest.fixture(scope="function")
def todo_ui_map(config):
    path_str = config["modules"]["microsoft_todo"]["resources"]["ui_map"]
    path = Path(path_str)
    # Fix path resolution (same logic as calculator_ui_map)
    if not path.is_absolute():
        repo_root = Path(__file__).resolve().parents[1]
        path = (repo_root / path).resolve()
    data = _load_json_file(path)
    return data.get("locators", data)



@pytest.fixture(scope="function")
def todo_app(todo_driver, todo_ui_map):
    from libs.drivers.app_session import AppSession
    return AppSession(todo_driver, todo_ui_map)


@pytest.fixture(scope="function")
def todo(todo_app):
    from libs.flows.windows.microsoft_todo import MicrosoftToDoFlows
    return MicrosoftToDoFlows(todo_app)
