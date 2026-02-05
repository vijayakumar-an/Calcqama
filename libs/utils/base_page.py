# libs/base_page.py
from __future__ import annotations

from typing import Dict, Tuple

from appium.webdriver.common.appiumby import AppiumBy
from libs.utils.waits import wait_visible, wait_clickable


_BY_MAP: Dict[str, str] = {
    "automationid": AppiumBy.ACCESSIBILITY_ID,
    "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
    "name": AppiumBy.NAME,
    "xpath": AppiumBy.XPATH,
    "id": AppiumBy.ID,
    "class_name": AppiumBy.CLASS_NAME,
}

Locator = Tuple[str, str]


def _normalize_locator_dict(locator: dict) -> Locator:
    if not isinstance(locator, dict):
        raise TypeError(f"Locator must be dict, got: {type(locator)}")

    # Case 1: explicit by/value
    if "by" in locator and "value" in locator:
        key = locator["by"].strip().lower()
        if key not in _BY_MAP:
            raise KeyError(f"Unsupported locator strategy: {locator['by']}")
        return _BY_MAP[key], locator["value"]

    # Case 2: nested {"locator": {...}}
    if "locator" in locator:
        inner = locator["locator"]
        for k in inner:
            key = k.strip().lower()
            if key in ("automationid", "automation_id"):
                return _BY_MAP["automationid"], inner[k]
            if key in _BY_MAP:
                return _BY_MAP[key], inner[k]
        raise KeyError(f"Unsupported nested locator keys: {inner.keys()}")

    # Case 3: flat locator
    for k, v in locator.items():
        key = k.strip().lower()
        if key in ("automationid", "automation_id"):
            return _BY_MAP["automationid"], v
        if key in _BY_MAP:
            return _BY_MAP[key], v

    raise KeyError(f"Cannot interpret locator: {locator}")


class BasePage:
    def __init__(self, driver, testdata: dict, timeouts: dict | None = None):
        self.driver = driver
        self.testdata = testdata
        self.timeouts = timeouts or {}
        self.default_wait = int(self.timeouts.get("explicit_wait_sec", 15))

    def _resolve(self, locator: dict) -> Locator:
        return _normalize_locator_dict(locator)

    def find(self, locator: dict, timeout=None):
        by, value = self._resolve(locator)
        return wait_visible(self.driver, by, value, timeout or self.default_wait)

    def click(self, locator: dict, timeout=None):
        by, value = self._resolve(locator)
        el = wait_clickable(self.driver, by, value, timeout or self.default_wait)
        el.click()
        return el

    def type(self, locator: dict, text: str, clear=True):
        el = self.find(locator)
        if clear:
            el.clear()
        el.send_keys(text)
        return el

    def text_of(self, locator: dict):
        el = self.find(locator)
        return (el.text or "").strip()

    def is_visible(self, locator: dict, timeout=3):
        try:
            self.find(locator, timeout)
            return True
        except Exception:
            return False
