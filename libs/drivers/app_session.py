# libs/drivers/app_session.py
from __future__ import annotations
import time
import re
from typing import Any, Dict, Optional

from appium import webdriver
from appium.options.windows import WindowsOptions


# =============================
# SESSION CREATION HELPERS
# =============================

def _resolve_module_cfg(config: dict, module_name: str) -> dict:
    return (config.get("modules", {}) or {}).get(module_name, {}) or {}


def _resolve_server_and_device(config: dict, module_cfg: dict):
    wa_global = config.get("winappdriver", {}) or {}
    wa_module = module_cfg.get("winappdriver", {}) or {}

    server = wa_module.get("server_url") or wa_global.get("server_url") or "http://127.0.0.1:4723"
    platform = wa_module.get("platformName") or wa_global.get("platformName") or "Windows"
    device = wa_module.get("deviceName") or wa_global.get("deviceName") or "WindowsPC"
    return server, platform, device


def _resolve_timeouts(config: dict, module_cfg: dict):
    t_global = config.get("timeouts", {}) or {}
    t_module = module_cfg.get("timeouts", {}) or {}
    implicit_wait = t_module.get("implicit_wait_sec", t_global.get("implicit_wait_sec", 2))
    new_cmd = t_module.get("new_command_timeout_sec", t_global.get("new_command_timeout_sec", 120))
    return implicit_wait, new_cmd


def _build_options(platform: str, device: str, timeout: int, app=None, window=None):
    opts = WindowsOptions()
    opts.set_capability("platformName", platform)
    opts.set_capability("appium:automationName", "Windows")
    opts.set_capability("appium:deviceName", device)
    opts.set_capability("appium:newCommandTimeout", timeout)

    if app:
        opts.set_capability("appium:app", app)
    if window:
        opts.set_capability("appium:appTopLevelWindow", window)

    return opts


def start_app(config: dict, module_name: str, *, retries=1, retry_wait_sec=1.0):
    module_cfg = _resolve_module_cfg(config, module_name)
    server, platform, device = _resolve_server_and_device(config, module_cfg)
    implicit_wait, new_cmd_timeout = _resolve_timeouts(config, module_cfg)

    # get app id/path
    app_cfg = module_cfg.get("app", {}) or {}
    app = app_cfg.get("app") or app_cfg.get("app_id") or app_cfg.get("app_path")
    if not app:
        raise ValueError(f"No app/app_id/app_path defined for module '{module_name}'")

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            opts = _build_options(platform, device, new_cmd_timeout, app=app)
            driver = webdriver.Remote(server, options=opts)
            driver.implicitly_wait(implicit_wait)
            return driver
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(retry_wait_sec)

    raise RuntimeError(f"Failed to create session for {module_name}: {last_err}") from last_err


def start_calculator(config: dict, retries=1, retry_wait_sec=1.0):
    return start_app(config, "calculator", retries=retries, retry_wait_sec=retry_wait_sec)


def safe_quit(driver):
    try:
        driver.quit()
    except Exception:
        pass


# =============================
# DEFAULT LOCATORS (fallbacks)
# =============================

# These are the standard AccessibilityIds for Windows Calculator (UWP).
# Your UI map (JSON) can override any of these. If a key is missing from
# the JSON, we fall back to this dict so tests keep working.
DEFAULT_LOCATORS: Dict[str, Dict[str, str]] = {
    # result reading
    "result": {"by": "accessibility id", "value": "CalculatorResults"},

    # digits
    "num_0": {"by": "accessibility id", "value": "num0Button"},
    "num_1": {"by": "accessibility id", "value": "num1Button"},
    "num_2": {"by": "accessibility id", "value": "num2Button"},
    "num_3": {"by": "accessibility id", "value": "num3Button"},
    "num_4": {"by": "accessibility id", "value": "num4Button"},
    "num_5": {"by": "accessibility id", "value": "num5Button"},
    "num_6": {"by": "accessibility id", "value": "num6Button"},
    "num_7": {"by": "accessibility id", "value": "num7Button"},
    "num_8": {"by": "accessibility id", "value": "num8Button"},
    "num_9": {"by": "accessibility id", "value": "num9Button"},

    # operators / keys
    "plus": {"by": "accessibility id", "value": "plusButton"},
    "minus": {"by": "accessibility id", "value": "minusButton"},
    "multiply": {"by": "accessibility id", "value": "multiplyButton"},
    "divide": {"by": "accessibility id", "value": "divideButton"},
    "equals": {"by": "accessibility id", "value": "equalButton"},
    "decimal_separator": {"by": "accessibility id", "value": "decimalSeparatorButton"},
    "clear": {"by": "accessibility id", "value": "clearButton"},
    "clear_entry": {"by": "accessibility id", "value": "clearEntryButton"},
    "backspace": {"by": "accessibility id", "value": "backSpaceButton"},
    "negate": {"by": "accessibility id", "value": "negateButton"},
    "percent": {"by": "accessibility id", "value": "percentButton"},

    # extra math (not used by your current -m addition set but provided)
    "square": {"by": "accessibility id", "value": "squareButton"},            # sometimes xpower2Button
    "sqrt": {"by": "accessibility id", "value": "squareRootButton"},
    "reciprocal": {"by": "accessibility id", "value": "inverseButton"},
}


# =============================
# FULL AppSession (Calculator)
# =============================

class AppSession:
    """
    Fully featured session wrapper for Calculator.
    Compatible with your CalculatorFlows.
    """

    def __init__(self, driver, ui_map: dict):
        self.driver = driver
        # Flatten nested "locators" if present
        if "locators" in ui_map and isinstance(ui_map["locators"], dict):
            self.ui = ui_map["locators"]
        else:
            self.ui = ui_map or {}

    # --------- locator resolution with fallback ---------

    def _get_locator(self, key: str) -> dict:
        loc = self.ui.get(key)
        if loc:
            return loc
        # fallback to default
        fallback = DEFAULT_LOCATORS.get(key)
        if not fallback:
            raise KeyError(f"Locator '{key}' not found in ui_map.")
        return fallback

    def click_button(self, key: str):
        loc = self._get_locator(key)
        elem = self.driver.find_element(loc["by"], loc["value"])
        elem.click()
        time.sleep(0.05)

    # --------- number entry ---------

    def press_number(self, value):
        """
        Press a full number like 123 or -5.6
        - If a leading '-' is present, enter digits then press Negate.
        """
        s = str(value)
        is_negative = s.startswith("-")
        if is_negative:
            s = s[1:]  # strip leading '-'

        for ch in s:
            if ch.isdigit():
                self.click_button(f"num_{ch}")
            elif ch == ".":
                self.click_button("decimal_separator")
            else:
                raise ValueError(f"Unsupported digit: {ch}")

        if is_negative:
            self.click_button("negate")

    # --------- operators ---------

    def press_operator(self, op: str):
        """
        op is one of: 'plus', 'minus', 'multiply', 'divide'
        """
        self.click_button(op)

    # --------- compute ---------

    def compute(self, a, op: str, b) -> str:
        self.clear()
        self.press_number(a)
        self.press_operator(op)
        self.press_number(b)
        self.click_button("equals")
        return self.get_result_value()

    # --------- result reading ---------

    def _clean_result_text(self, raw: str) -> str:
        """
        Windows Calculator returns text like:
          "Display is  42"
          "Display is  0.3"
        We strip the "Display is" prefix and any commas, NBSPs, LRM/RLM.
        """
        if not raw:
            return ""
        txt = raw
        txt = txt.replace("Display is", "")
        txt = txt.replace(",", "")
        txt = txt.replace("\u200f", "").replace("\u200e", "").replace("\xa0", "")
        txt = txt.strip()

        # As a last guard, extract the last number-like token
        m = re.findall(r"-?\d+(?:\.\d+)?", txt)
        if m:
            return m[-1]
        return txt

    def get_result_value(self) -> str:
        loc = self._get_locator("result")
        elem = self.driver.find_element(loc["by"], loc["value"])
        return self._clean_result_text(elem.text)

    def get_result_raw(self) -> str:
        loc = self._get_locator("result")
        elem = self.driver.find_element(loc["by"], loc["value"])
        return elem.text or ""

    # --------- clear ---------

    def clear(self):
        try:
            self.click_button("clear")
        except Exception:
            # if clear fails due to state, ignore
            pass

    # --------- section-based helpers (for nav/settings/history) ---------
    # Your -m addition tests won't call these, but flows include them, so keep them.

    def _get_section_locator(self, section: str, key: str) -> dict:
        # support nested maps like ui['history']['empty_text'] if present
        sec = self.ui.get(section)
        if isinstance(sec, dict) and key in sec:
            return sec[key]
        # otherwise, no default fallback for sections (these vary by version)
        raise KeyError(f"Locator '{section}.{key}' not found in ui_map.")

    def click_in(self, section: str, key: str):
        loc = self._get_section_locator(section, key)
        elem = self.driver.find_element(loc["by"], loc["value"])
        elem.click()
        time.sleep(0.05)

    def exists_in(self, section: str, key: str, timeout=1.0) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            try:
                loc = self._get_section_locator(section, key)
                self.driver.find_element(loc["by"], loc["value"])
                return True
            except Exception:
                time.sleep(0.1)
        return False

    def get_text_in(self, section: str, key: str) -> str:
        loc = self._get_section_locator(section, key)
        elem = self.driver.find_element(loc["by"], loc["value"])
        return (elem.text or "").strip()