from __future__ import annotations
import time
from libs.drivers.app_session import AppSession


class MicrosoftToDoFlows:
    """
    High-level reusable flows for Microsoft To Do
    """

    def __init__(self, app: AppSession) -> None:
        self.app = app

    # =============================
    # Window Controls
    # =============================

    def maximize(self):
        self.app.click_in("display", "maximize_btn")

    def minimize(self):
        self.app.click_in("display", "minimize_btn")

    def close(self):
        self.app.click_in("display", "close_btn")

    # =============================
    # Navigation Menus
    # =============================

    def open_my_day(self):
        self.app.click_in("menus", "My_day_menu")

    def open_important(self):
        self.app.click_in("menus", "important_menu")

    def open_assigned_to_me(self):
        self.app.click_in("menus", "Assigned_to_me_menu")

    def open_flagged_email(self):
        self.app.click_in("menus", "Flagged_email_menu")

    def open_planned(self):
        self.app.click_in("menus", "planned_menu")

    def open_tasks(self):
        self.app.click_in("menus", "tasks_menu")

    # =============================
    # My Day Section
    # =============================

    def keep_on_top(self):
        self.app.click_in("MyDay_menu", "keep_on_top_btn")

    def back_to_fullview(self):
        self.app.click_in("MyDay_menu", "back_to_fullview_btn")

    def open_suggestions(self):
        self.app.click_in("MyDay_menu", "suggestions_btn")

    def click_add_task(self):
        self.app.click_in("MyDay_menu", "add_task_btn")

    def view_task_details(self):
        self.app.click_in("MyDay_menu", "view_task_details")

    def verify_created_task_visible(self):
        return self.app.exists_in("MyDay_menu", "Created_Task", timeout=5)

    def dismiss_detail_view(self):
        self.app.click_in("MyDay_menu", "Dismiss_Detail_View_Button")


    # =============================
    # Profile Section
    # =============================

    def open_profile(self):
        self.app.click_in("profile", "profile_btn")

    def manage_accounts(self):
        self.app.click_in("profile", "manage_acc")

    def open_settings(self):
        self.app.click_in("profile", "settings")

    # =============================
    # Example Flow
    # =============================

    def open_myday_and_add_task(self):
        self.open_my_day()
        time.sleep(1)
        self.click_add_task()


    def create_new_list(self):
        self.app.click_in("New_List", "New_List_Button")

    def verify_last_created_list(self):
        return self.app.exists_in("New_List", "Last_Created_List", timeout=5)

    def add_task_to_current_list(self, task_name: str):
        self.app.click_in("New_List", "Add_Task_Textbox")
        self.app.driver.switch_to.active_element.send_keys(task_name)
        from selenium.webdriver.common.keys import Keys
        self.app.driver.switch_to.active_element.send_keys(Keys.ENTER)

    def edit_task(self, new_text: str):
        self.app.click_in("New_List", "Edit_Task_TextBox")
        elem = self.app.driver.switch_to.active_element
        elem.clear()
        elem.send_keys(new_text)

    def print_list(self):
        self.app.click_in("New_List", "Print_List_MenuItem")

    def delete_list(self):
        self.app.click_in("New_List", "Delete_List_MenuItem")
