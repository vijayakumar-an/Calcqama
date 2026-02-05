# libs/drivers/windows_driver.py
from appium import webdriver
from appium.options.windows import WindowsOptions


def create_windows_driver(config: dict, module_name: str):
    """
    Creates a Windows driver for Appium 3.x using the Appium Windows Driver.
    Uses W3C namespaced vendor capabilities (appium:*).
    """

    # --- Resolve module/global config ---
    modules = config.get("modules", {}) or {}
    module_cfg = modules.get(module_name, {}) or {}
    wa_global = config.get("winappdriver", {}) or {}   # keeping the block name for backward-compat
    wa_module = module_cfg.get("winappdriver", {}) or {}

    server_url = wa_module.get("server_url") or wa_global.get("server_url") or "http://127.0.0.1:4723"
    platform_name = wa_module.get("platformName") or wa_global.get("platformName") or "Windows"
    device_name = wa_module.get("deviceName") or wa_global.get("deviceName") or "WindowsPC"

    # --- App selection ---
    app_cfg = module_cfg.get("app", {}) or {}
    app_val = app_cfg.get("app") or app_cfg.get("app_id") or app_cfg.get("app_path")
    if not app_val:
        raise ValueError(f"No app/app_id/app_path defined for module '{module_name}'")

    # --- Timeouts ---
    t_global = config.get("timeouts", {}) or {}
    t_module = module_cfg.get("timeouts", {}) or {}
    implicit_wait = t_module.get("implicit_wait_sec", t_global.get("implicit_wait_sec", 2))
    new_cmd_timeout = t_module.get("new_command_timeout_sec", t_global.get("new_command_timeout_sec", 120))

    # --- Build Appium 3 capabilities (namespaced) ---
    opts = WindowsOptions()
    opts.set_capability("platformName", platform_name)               # Standard W3C key
    opts.set_capability("appium:automationName", "Windows")          # Namespaced vendor keys
    opts.set_capability("appium:deviceName", device_name)
    opts.set_capability("appium:app", app_val)
    opts.set_capability("appium:newCommandTimeout", new_cmd_timeout)

    # --- Create driver ---
    driver = webdriver.Remote(command_executor=server_url, options=opts)
    driver.implicitly_wait(implicit_wait)
    return driver