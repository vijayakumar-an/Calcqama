from libs.utils.base_page import BasePage
from libs.utils.assertions import assert_true


class EnergyConsumptionPage(BasePage):
    @property
    def L(self):
        return self.testdata["locators"]["energy_consumption"]

    @property
    def NAV(self):
        return self.testdata["locators"]["nav"]

    def open_energy_consumption(self):
        self.click(self.NAV["energy_consumption_tab"])
        assert_true(self.is_visible(self.L["page_header"], timeout=10),
                    "Energy Consumption page header not visible")

    def set_period(self, period_name: str):
        self.click(self.L["period_dropdown"])
        key_map = {
            "Today": "period_today",
            "This Week": "period_week",
            "This Month": "period_month",
            "This Year": "period_year",
            "Custom": "period_custom",
        }
        self.click(self.L[key_map[period_name]])

    def set_unit(self, unit: str):
        self.click(self.L["unit_toggle"])
        if unit == "kWh":
            self.click(self.L["unit_kwh"])
        elif unit == "Wh":
            self.click(self.L["unit_wh"])
        else:
            raise ValueError(f"Unsupported unit: {unit}")

    def set_chart_type(self, chart: str):
        self.click(self.L["chart_type_dropdown"])
        if chart == "Line":
            self.click(self.L["chart_type_line"])
        elif chart == "Bar":
            self.click(self.L["chart_type_bar"])
        elif chart == "Area":
            self.click(self.L["chart_type_area"])
        else:
            raise ValueError(f"Unsupported chart: {chart}")

    def set_device(self, device_name: str):
        self.click(self.L["device_filter_dropdown"])
        if device_name == "All devices":
            self.click(self.L["device_all"])
        else:
            self.click({"by": "name", "value": device_name})

    def apply_filters(self):
        self.click(self.L["apply_filters_btn"])

    def reset_filters(self):
        self.click(self.L["reset_filters_btn"])

    def set_custom_range(self, from_date: str, to_date: str):
        self.set_period("Custom")
        if from_date is not None:
            self.type(self.L["custom_from_date"], from_date)
        if to_date is not None:
            self.type(self.L["custom_to_date"], to_date)

    def export(self, export_type: str):
        self.click(self.L["export_btn"])
        if export_type == "CSV":
            self.click(self.L["export_csv"])
        elif export_type == "PDF":
            self.click(self.L["export_pdf"])
        elif export_type == "XLSX":
            self.click(self.L["export_xlsx"])
        else:
            raise ValueError(f"Unsupported export: {export_type}")

    def get_total_consumption_text(self):
        return self.text_of(self.L["summary_total_kwh"])

    def get_cost_text(self):
        return self.text_of(self.L["summary_cost"])

    def chart_visible(self):
        return self.is_visible(self.L["chart_container"], timeout=8)

    def toast_text(self):
        if self.is_visible(self.L["toast_message"], timeout=2):
            return self.text_of(self.L["toast_message"])
        return ""

    def has_error(self):
        return self.is_visible(self.L["error_banner"], timeout=2)
