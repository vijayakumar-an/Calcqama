def assert_non_empty(value, msg="Expected non-empty value"):
    assert value is not None and str(value).strip() != "", msg


def assert_contains(text, expected, msg=None):
    assert expected in text, msg or f"Expected '{expected}' in '{text}'"


def assert_true(cond, msg="Expected condition to be True"):
    assert cond, msg
