# libs/flows/calculator.py
from __future__ import annotations

import time
from typing import Iterable, Union

from libs.drivers.app_session import AppSession

Number = Union[int, float]


class CalculatorFlows:
    """
    High-level reusable actions for Windows Calculator (Standard mode).
    """

    def __init__(self, app: AppSession) -> None:
        self.app = app

    # ---------- basic arithmetic ----------

    def add(self, a: Number, b: Number) -> str:
        return self.app.compute(a, "plus", b)

    def subtract(self, a: Number, b: Number) -> str:
        return self.app.compute(a, "minus", b)

    def multiply(self, a: Number, b: Number) -> str:
        return self.app.compute(a, "multiply", b)

    def divide(self, a: Number, b: Number) -> str:
        return self.app.compute(a, "divide", b)

    # ---------- sequences / expression ----------

    def press_keys(self, keys: Iterable[str]) -> str:
        self.app.clear()
        for k in keys:
            self.app.click_button(k)
        return self.app.get_result_value()

    def compute_expression(self, expression: str) -> str:
        self.app.clear()
        op_map = {"+": "plus", "-": "minus", "*": "multiply", "/": "divide", "=": "equals"}
        for ch in expression:
            if ch.isdigit():
                self.app.click_button(f"num_{ch}")
            elif ch == ".":
                self.app.click_button("decimal_separator")
            elif ch in op_map:
                self.app.click_button(op_map[ch])
            else:
                raise ValueError(f"Unsupported character in expression: {ch!r}")
        if not expression.endswith("="):
            self.app.click_button("equals")
        return self.app.get_result_value()

    # ---------- special keys & unary ops ----------

    def clear(self) -> None:
        self.app.clear()

    def clear_entry(self) -> None:
        self.app.click_button("clear_entry")

    def backspace(self) -> None:
        self.app.click_button("backspace")

    def negate(self) -> None:
        self.app.click_button("negate")

    def decimal(self) -> None:
        self.app.click_button("decimal_separator")

    def equals(self) -> None:
        self.app.click_button("equals")

    def square(self) -> str:
        self.app.click_button("square")
        time.sleep(0.1)
        return self.app.get_result_value()

    def sqrt(self) -> str:
        self.app.click_button("sqrt")
        time.sleep(0.1)
        return self.app.get_result_value()

    def reciprocal(self) -> str:
        self.app.click_button("reciprocal")
        time.sleep(0.1)
        return self.app.get_result_value()

    def percent_after_op(self, a: Number, op: str, b: Number) -> str:
        """
        Standard-mode percent:
          200 * 10% = 20
          50 + 10%  = 55
          50 - 10%  = 45
        """
        self.app.clear()
        self.app.press_number(a)
        self.app.press_operator(op)
        self.app.press_number(b)
        self.app.click_button("percent")
        self.app.click_button("equals")
        time.sleep(0.2)
        return self.app.get_result_value()

    def repeated_equals(self, a: Number, op: str, b: Number, repeats: int = 1) -> str:
        """
        Example: 5 + 5 = = -> 15 (adds 5 again)
        """
        self.app.clear()
        self.app.press_number(a)
        self.app.press_operator(op)
        self.app.press_number(b)
        self.app.click_button("equals")
        for _ in range(max(0, repeats)):
            self.app.click_button("equals")
        time.sleep(0.2)
        return self.app.get_result_value()

    def chain_immediate_execution(self) -> str:
        """
        Standard mode immediate execution:
          2 + 3 * 4 = -> (2+3)*4 = 20
        """
        self.app.clear()
        self.app.press_number(2)
        self.app.press_operator("plus")
        self.app.press_number(3)
        self.app.press_operator("multiply")
        self.app.press_number(4)
        self.app.click_button("equals")
        return self.app.get_result_value()

    def lead_zeros_sum_12_plus_30(self) -> str:
        """
        Enter leading zeros before numbers:
          00012 + 00030 = 42
        """
        self.app.clear()
        for _ in range(3):
            self.app.click_button("num_0")
        self.app.press_number(12)
        self.app.press_operator("plus")
        for _ in range(3):
            self.app.click_button("num_0")
        self.app.press_number(30)
        self.app.click_button("equals")
        return self.app.get_result_value()

    def decimal_point_once(self) -> str:
        """
        Press '.' twice and ensure only one decimal point is used:
          '.' '.' '5' '=' -> 0.5
        """
        self.app.clear()
        self.app.click_button("decimal_separator")
        self.app.click_button("decimal_separator")  # should be ignored by app
        self.app.press_number(5)
        self.app.click_button("equals")
        return self.app.get_result_value()

    def raw_result_contains(self, needle: str) -> bool:
        return needle.lower() in self.app.get_result_raw().lower()

    # ---------- memory operations ----------

    def mem_clear(self) -> None:
        self.app.click_button("mem_clear")

    def mem_store_current(self) -> None:
        self.app.click_button("mem_store")

    def mem_recall(self) -> None:
        self.app.click_button("mem_recall")

    def mem_add_current(self) -> None:
        self.app.click_button("mem_add")

    def mem_subtract_current(self) -> None:
        self.app.click_button("mem_subtract")

    def store_value(self, value: Number) -> None:
        self.app.clear()
        self.app.press_number(value)
        self.mem_store_current()

    def recall_to_result(self) -> str:
        """
        Recall memory into entry and return display value.
        """
        self.app.clear()
        self.mem_recall()
        return self.app.get_result_value()

    # ---------- navigation / history / settings ----------

    def open_navigation(self) -> None:
        self.app.click_in("nav", "menu")

    def select_mode_standard(self) -> None:
        self.open_navigation()
        self.app.click_in("nav", "menu_item_standard")

    def open_history(self) -> None:
        self.app.click_in("nav", "history")

    def history_is_empty(self) -> bool:
        try:
            txt = self.app.get_text_in("history", "empty_text")
            return "history" in txt.lower()
        except Exception:
            return False

    def history_has_items_after_calc(self) -> bool:
        # Create a history entry, then check pane
        self.add(1, 1)
        self.open_history()
        return not self.history_is_empty()

    def open_settings(self) -> None:
        self.open_navigation()
        self.app.click_in("nav", "menu_item_settings")

    def settings_theme_options_present(self) -> bool:
        if not self.app.exists_in("settings", "header", timeout=3.0):
            return False
        present = all(
            [
                self.app.exists_in("settings", "theme_expander", timeout=3.0),
                self.app.exists_in("settings", "theme_light", timeout=3.0),
                self.app.exists_in("settings", "theme_dark", timeout=3.0),
                self.app.exists_in("settings", "theme_system", timeout=3.0),
            ]
        )
        return present