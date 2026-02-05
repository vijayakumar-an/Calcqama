# tests/modules/calculator/testsuite.py
import pytest

pytestmark = pytest.mark.calculator  # Run with: pytest -m calculator


class TestSuiteCalculator:
    """
    Suite: Windows Calculator – Standard mode, functions, history, settings, and memory
    Preconditions:
        - WinAppDriver running at http://127.0.0.1:4723
        - Windows Calculator installed / accessible by AppId
        - UI map matches local build (resources/ui_map/windows/calculator.json)
    Notes:
        - Each test starts from cleared display (fixtures do this).
        - Results are normalized numeric strings via get_result_value().
        - For error conditions we assert on raw text using raw_result_contains().
    """

    # ---------------- Basic Arithmetic ----------------

    @pytest.mark.basic
    @pytest.mark.addition
    def test_CALC_001_addition_simple_12_plus_30_equals_42(self, calc):
        """
        Test ID: CALC-001
        Title  : Addition – 12 + 30 = 42
        Purpose: Validate basic addition.
        Steps  : 12 + 30 =
        Expected: '42'
        """
        assert calc.add(12, 30) == "42"

    @pytest.mark.basic
    @pytest.mark.addition
    def test_CALC_002_addition_multi_digit_1234_plus_5678_equals_6912(self, calc):
        """
        Test ID: CALC-002
        Title  : Addition - 1234 + 5678 = 6912
        Purpose: Ensure multi-digit entry and carry work.
        Steps  : 1234 + 5678 =
        Expected: '6912'
        """
        assert calc.add(1234, 5678) == "6912"

    @pytest.mark.basic
    @pytest.mark.subtraction
    def test_CALC_003_subtraction_100_minus_58_equals_42(self, calc):
        """
        Test ID: CALC-003
        Title  : Subtraction – 100 - 58 = 42
        Purpose: Validate subtraction with borrow.
        Steps  : 100 - 58 =
        Expected: '42'
        """
        assert calc.subtract(100, 58) == "42"

    @pytest.mark.basic
    @pytest.mark.multiplication
    def test_CALC_004_multiplication_6_times_7_equals_42(self, calc):
        """
        Test ID: CALC-004
        Title  : Multiplication – 6 × 7 = 42
        Purpose: Validate multiplication.
        Steps  : 6 * 7 =
        Expected: '42'
        """
        assert calc.multiply(6, 7) == "42"

    @pytest.mark.basic
    @pytest.mark.division
    def test_CALC_005_division_84_divided_by_2_equals_42(self, calc):
        """
        Test ID: CALC-005
        Title  : Division – 84 / 2 = 42
        Purpose: Validate division.
        Steps  : 84 / 2 =
        Expected: '42'
        """
        assert calc.divide(84, 2) == "42"

    # ---------------- Expression / Sequence helpers ----------------

    @pytest.mark.expression
    def test_CALC_006_expression_string_12_plus_30(self, calc):
        """
        Test ID: CALC-006
        Title  : Expression – '12+30'
        Purpose: Expression parsing to key presses.
        Steps  : Evaluate '12+30' (framework adds '=')
        Expected: '42'
        """
        assert calc.compute_expression("12+30") == "42"

    @pytest.mark.sequence
    def test_CALC_007_explicit_key_sequence_equals_42(self, calc):
        """
        Test ID: CALC-007
        Title  : Sequence – keys -> 42
        Purpose: Validate UI-map key-by-key execution.
        Steps  : ['num_1','num_2','plus','num_3','num_0','equals']
        Expected: '42'
        """
        keys = ["num_1", "num_2", "plus", "num_3", "num_0", "equals"]
        assert calc.press_keys(keys) == "42"

    # ---------------- UI / Navigation / Settings / History ----------------

    @pytest.mark.navigation
    def test_CALC_008_open_navigation_and_select_standard_mode(self, calc):
        """
        Test ID: CALC-008
        Title  : Navigation – open and select 'Standard'
        Purpose: Ensure hamburger menu opens and Standard mode is selectable.
        Steps  : Open menu -> click 'Standard'
        Expected: No error during interaction.
        """
        calc.select_mode_standard()

    @pytest.mark.history
    def test_CALC_009_history_contains_entry_after_calculation(self, calc):
        """
        Test ID: CALC-009
        Title  : History – non-empty after a calc
        Purpose: Verify that performing a calc adds an entry to History.
        Steps  : Do 1+1= -> open History -> check not empty
        Expected: True (has items)
        """
        assert calc.history_has_items_after_calc() is True

    @pytest.mark.settings
    def test_CALC_010_open_settings_and_verify_theme_options(self, calc):
        """
        Test ID: CALC-010
        Title  : Settings – Theme options presence
        Purpose: Ensure 'App theme' expander and 3 options exist.
        Steps  : Open Settings -> verify Light/Dark/System options present
        Expected: True
        """
        calc.open_settings()
        assert calc.settings_theme_options_present() is True

    # ---------------- Decimals / Negatives / Edge cases ----------------

    @pytest.mark.decimal
    @pytest.mark.addition
    def test_CALC_011_decimal_addition_point1_plus_point2_equals_point3(self, calc):
        """
        Test ID: CALC-011
        Title  : Decimal – 0.1 + 0.2 = 0.3
        Purpose: Validate decimal arithmetic.
        Steps  : 0.1 + 0.2 =
        Expected: '0.3'
        """
        assert calc.add(0.1, 0.2) == "0.3"

    @pytest.mark.decimal
    @pytest.mark.negative
    @pytest.mark.addition
    def test_CALC_012_negative_plus_decimal(self, calc):
        """
        Test ID: CALC-012
        Title  : Negative + Decimal – (-10.5) + 0.5 = -10
        Purpose: Validate negative and decimal input.
        Steps  : -10.5 + 0.5 =
        Expected: '-10'
        """
        assert calc.add(-10.5, 0.5) == "-10"

    @pytest.mark.error
    @pytest.mark.division
    def test_CALC_013_divide_by_zero_shows_error_text(self, calc):
        """
        Test ID: CALC-013
        Title  : Division by zero – error message
        Purpose: Ensure user-friendly error text is shown.
        Steps  : 10 / 0 =
        Expected: Raw result contains 'cannot' (e.g., 'Cannot divide by zero')
        """
        _ = calc.divide(10, 0)
        assert calc.raw_result_contains("cannot")

    @pytest.mark.unary
    @pytest.mark.decimal
    def test_CALC_014_reciprocal_of_ten_is_point1(self, calc):
        """
        Test ID: CALC-014
        Title  : Reciprocal – 1/10 = 0.1
        Purpose: Validate 1/x.
        Steps  : 10 -> 1/x
        Expected: '0.1'
        """
        calc.clear()
        calc.app.press_number(10)
        assert calc.reciprocal() == "0.1"

    @pytest.mark.unary
    def test_CALC_015_square_of_12_is_144(self, calc):
        """
        Test ID: CALC-015
        Title  : Square – 12² = 144
        Purpose: Validate x².
        Steps  : 12 -> x²
        Expected: '144'
        """
        calc.clear()
        calc.app.press_number(12)
        assert calc.square() == "144"

    @pytest.mark.unary
    def test_CALC_016_sqrt_of_81_is_9(self, calc):
        """
        Test ID: CALC-016
        Title  : Square root – √81 = 9
        Purpose: Validate √x.
        Steps  : 81 -> √
        Expected: '9'
        """
        calc.clear()
        calc.app.press_number(81)
        assert calc.sqrt() == "9"

    @pytest.mark.unary
    @pytest.mark.input
    def test_CALC_017_negate_toggles_sign(self, calc):
        """
        Test ID: CALC-017
        Title  : Negate – 5 -> +/- = -5
        Purpose: Validate sign toggle.
        Steps  : 5 -> +/-
        Expected: '-5'
        """
        calc.clear()
        calc.app.press_number(5)
        calc.negate()
        assert calc.app.get_result_value() == "-5"

    @pytest.mark.input
    def test_CALC_018_backspace_removes_last_digit(self, calc):
        """
        Test ID: CALC-018
        Title  : Backspace – 123 -> ⌫ = 12
        Purpose: Validate digit deletion.
        Steps  : Enter 123 -> ⌫
        Expected: '12'
        """
        calc.clear()
        calc.app.press_number(123)
        calc.backspace()
        assert calc.app.get_result_value() == "12"

    @pytest.mark.input
    @pytest.mark.ce
    def test_CALC_019_clear_entry_keeps_accumulator(self, calc):
        """
        Test ID: CALC-019
        Title  : CE – keeps accumulator
        Purpose: CE clears only current entry, not pending accumulator.
        Steps  : 12 + 34, CE, 56, =
        Expected: '68'
        """
        calc.clear()
        calc.app.press_number(12)
        calc.app.press_operator("plus")
        calc.app.press_number(34)
        calc.clear_entry()
        calc.app.press_number(56)
        calc.equals()
        assert calc.app.get_result_value() == "68"

    @pytest.mark.input
    @pytest.mark.c
    def test_CALC_020_clear_all_resets_to_zero(self, calc):
        """
        Test ID: CALC-020
        Title  : C – full reset to zero
        Purpose: Validate 'C' clears everything.
        Steps  : Enter 99 -> C
        Expected: '0'
        """
        calc.clear()
        calc.app.press_number(99)
        calc.clear()
        assert calc.app.get_result_value() == "0"

    # ---------------- Percent behavior ----------------

    @pytest.mark.percent
    @pytest.mark.multiplication
    def test_CALC_021_percent_multiply_200_times_10percent_equals_20(self, calc):
        """
        Test ID: CALC-021
        Title  : Percent (multiply) – 200 * 10% = 20
        Purpose: Validate percent applied to first operand with multiply.
        Steps  : 200 * 10 % =
        Expected: '20'
        """
        assert calc.percent_after_op(200, "multiply", 10) == "20"

    @pytest.mark.percent
    @pytest.mark.addition
    def test_CALC_022_percent_add_50_plus_10percent_equals_55(self, calc):
        """
        Test ID: CALC-022
        Title  : Percent (add) – 50 + 10% = 55
        Purpose: Validate percent add behavior.
        Steps  : 50 + 10 % =
        Expected: '55'
        """
        assert calc.percent_after_op(50, "plus", 10) == "55"

    @pytest.mark.percent
    @pytest.mark.subtraction
    def test_CALC_023_percent_subtract_50_minus_10percent_equals_45(self, calc):
        """
        Test ID: CALC-023
        Title  : Percent (subtract) – 50 - 10% = 45
        Purpose: Validate percent subtract behavior.
        Steps  : 50 - 10 % =
        Expected: '45'
        """
        assert calc.percent_after_op(50, "minus", 10) == "45"

    # ---------------- Equals & order of operations ----------------

    @pytest.mark.equals
    def test_CALC_024_repeated_equals_repeats_last_operation(self, calc):
        """
        Test ID: CALC-024
        Title  : Repeated '=' – 5 + 5 == -> 15
        Purpose: Validate that '=' repeats the last op with last operand.
        Steps  : 5 + 5 = =
        Expected: '15'
        """
        assert calc.repeated_equals(5, "plus", 5, repeats=1) == "15"

    @pytest.mark.equals
    @pytest.mark.immediate_execution
    def test_CALC_025_chain_immediate_execution_2_plus_3_times_4_equals_20(self, calc):
        """
        Test ID: CALC-025
        Title  : Immediate execution – (2+3)*4 = 20
        Purpose: Standard mode is immediate, not algebraic precedence.
        Steps  : 2 + 3 * 4 =
        Expected: '20'
        """
        assert calc.chain_immediate_execution() == "20"

    # ---------------- Input quirks ----------------

    @pytest.mark.input
    @pytest.mark.leading_zeros
    def test_CALC_026_leading_zeros_are_ignored_in_value(self, calc):
        """
        Test ID: CALC-026
        Title  : Leading zeros – 00012 + 00030 = 42
        Purpose: Validate leading zeros handled gracefully.
        Steps  : 00012 + 00030 =
        Expected: '42'
        """
        assert calc.lead_zeros_sum_12_plus_30() == "42"

    @pytest.mark.input
    @pytest.mark.decimal
    def test_CALC_027_double_decimal_keeps_single_point(self, calc):
        """
        Test ID: CALC-027
        Title  : Decimal pressed twice – result 0.5
        Purpose: Only one decimal point should be used.
        Steps  : '.' '.' 5 '='
        Expected: '0.5'
        """
        assert calc.decimal_point_once() == "0.5"

    @pytest.mark.unary
    @pytest.mark.error
    def test_CALC_028_reciprocal_of_zero_shows_error(self, calc):
        """
        Test ID: CALC-028
        Title  : Reciprocal(0) – error text
        Purpose: Validate divide-by-zero via 1/x.
        Steps  : 0 -> 1/x
        Expected: Raw result contains 'cannot'
        """
        calc.clear()
        calc.app.press_number(0)
        _ = calc.reciprocal()
        assert calc.raw_result_contains("cannot")

    # ---------------- Memory operations ----------------

    @pytest.mark.memory
    @pytest.mark.ms
    @pytest.mark.mr
    def test_CALC_029_memory_store_and_recall_42(self, calc):
        """
        Test ID: CALC-029
        Title  : Memory – store 42 and recall
        Purpose: Validate MS and MR.
        Steps  : Enter 42 -> MS -> C -> MR
        Expected: '42'
        """
        calc.store_value(42)
        calc.clear()
        assert calc.recall_to_result() == "42"

    @pytest.mark.memory
    @pytest.mark.mplus
    @pytest.mark.mr
    def test_CALC_030_memory_add_then_recall(self, calc):
        """
        Test ID: CALC-030
        Title  : Memory – M+ adds to stored value
        Purpose: Validate M+.
        Steps  : MS 10 -> Enter 5 -> M+ -> MR
        Expected: '15'
        """
        calc.store_value(10)
        calc.app.press_number(5)
        calc.mem_add_current()
        assert calc.recall_to_result() == "15"

    @pytest.mark.memory
    @pytest.mark.mminus
    @pytest.mark.mr
    def test_CALC_031_memory_subtract_then_recall(self, calc):
        """
        Test ID: CALC-031
        Title  : Memory – M- subtracts from stored value
        Purpose: Validate M-.
        Steps  : From 15 in memory -> Enter 3 -> M- -> MR
        Expected: '12'
        """
        # If run independently, initialize memory to 15
        calc.store_value(15)
        calc.app.press_number(3)
        calc.mem_subtract_current()
        assert calc.recall_to_result() == "12"

    @pytest.mark.memory
    @pytest.mark.mc
    def test_CALC_032_memory_clear_empties_recall(self, calc):
        """
        Test ID: CALC-032
        Title  : Memory - MC clears memory
        Purpose: After MC, MR should not inject prior value.
        Steps  : Store 9 -> MC -> C -> MR
        Expected: '0'
        """
        calc.store_value(9)
        calc.mem_clear()
        calc.clear()
        calc.mem_recall()
        assert calc.app.get_result_value() == "0"