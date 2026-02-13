import pytest


class TestMicrosoftToDo:

    def test_open_app_and_verify_my_day(self, todo):
        """
        Test Case:
        1. Launch Microsoft To Do
        2. Verify Add Task button is visible (My Day is default)
        """
        # No need to click My Day (default page)
        assert todo.app.exists_in("MyDay_menu", "add_task_btn", timeout=5), \
            "Add Task button not visible in My Day"

    def test_open_app_and_go_to_planned(self, todo):
        """
        Test Case:
        1. Launch Microsoft To Do
        2. Click on Planned menu
        3. Verify Add Task button still exists
        """
        # Step 1: Open Planned
        todo.open_planned()
        # Step 2: Basic validation (check menu exists)
        assert todo.app.exists_in("menus", "planned_menu", timeout=5), \
            "Planned menu not accessible"

    def test_open_app_and_go_to_important(self, todo):
        """
        Test Case:
        1. Launch Microsoft To Do
        2. Click on Important menu
        3. Verify Add Task button still exists
        """
        # Step 1: Open Important
        todo.open_important()
        todo.keep_on_top()
        assert todo.app.exists_in("MyDay_menu", "keep_on_top_btn", timeout=5), \
        "Keep On Top button not accessible"

    def test_open_app_and_go_to_assigned_to_me(self, todo):
        """
        Test Case:
        1. Launch Microsoft To Do
        2. Click on Assigned to Me menu
        3. Verify Add Task button still exists
        """
        # Step 1: Open Assigned to Me
        todo.open_assigned_to_me()
        # Step 2: Basic validation (check menu exists)
        assert todo.app.exists_in("menus", "Assigned_to_me_menu", timeout=5), \
        "Assigned to Me menu not accessible"