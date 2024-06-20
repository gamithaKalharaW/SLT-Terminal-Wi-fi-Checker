from os import getenv
from pathlib import Path

import click
from dotenv import dotenv_values


import time
from datetime import date
import ttkbootstrap as ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


# NOTE: to be synced with pyproject.toml version field
__version__ = "0.1.3"

HELP = """
===== PyWiCh ===== 
This is a terminal application meant to be used with MySLT portal
The following options are implemented:
    --help       Show this help message
    --version    Show application version
"""


@click.command()
@click.version_option(version=__version__, prog_name="PyWiCh")
@click.help_option(HELP)
def main_app():
    driver_path = Path(getenv("HOMEPATH")).resolve() / "chromedriver.exe"

    profile_path = Path(getenv("HOMEPATH")).resolve() / ".pywich"
    if profile_path.exists():
        print("Profile config found")
        values = dotenv_values(profile_path)
        username: str = values["NAME"]
        password: str = values["PASSWORD"]
        check_wifi(username, password, driver_path)

    else:
        print("Profile config not found")
        print("Creating profile config")
        profile_path.touch()
        name = input("Enter username: ")
        password = input("Enter password: ")
        write_string = f"NAME={name}\nPASSWORD={password}"
        profile_path.write_text(write_string)
        print("Profile created, re-run command to execute")


# util funcs
def check_wifi(username: str, password: str, driver_path: str | Path):

    scriptdir = Path(__file__).parent
    wifi_data = get_usage(
        username=username, password=password, driver_path=driver_path
    )
    date_data = get_date()
    app = App(
        size=(850, 450),
        wifi_data=wifi_data,
        date_data=date_data,
        # iconphoto=str(scriptpath.parent/'dump/wifi-checker-terminal/Eye_Fi_icon.png')
        # iconphoto=str(
        #     scriptpath / "../dump/wifi-checker-terminal/Eye_Fi_Center_icon.png"
        # ),
        iconphoto=scriptdir.parent / "assets/g6.png",
    )
    app.place_window_center()
    app.focus_set()
    app.focus()
    app.mainloop()


def get_usage(
    username: str | None = None,
    password: str | None = None,
    driver_path: str | None = None,
):
    def get_element(opt: str, path: str, driver):
        repeats = 0
        ele = None
        while repeats < 20:
            try:
                ele = driver.find_element(opt, path)
                break
            except Exception:
                time.sleep(0.5)
                repeats += 1
        return ele

    site_url = "https://myslt.slt.lk"
    # INFO: this is where the problem is
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # INFO: posible fix
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    print(f"Starting '{site_url}'...")
    driver.get(site_url)
    print(f"Started '{site_url}'")

    USERNAME = username
    PASSWORD = password

    name_input = get_element(
        "xpath", '//*[@id="root"]/div/div[2]/div[2]/div[1]/div[1]/input', driver
    )
    name_input.send_keys(USERNAME)

    pass_input = get_element(
        "xpath", '//*[@id="root"]/div/div[2]/div[2]/div[1]/div[2]/input', driver
    )
    pass_input.send_keys(PASSWORD)

    sign_btn = get_element(
        "xpath", '//*[@id="root"]/div/div[2]/div[2]/div[2]/button', driver
    )
    sign_btn.click()

    pop_up = get_element("xpath", "/html/body/div[6]/div/div/span/i", driver)
    if pop_up is not None:
        pop_up.click()

    used_amount1 = get_element(
        "xpath",
        "/html/body/div[1]/div/div/div[6]/div[3]/div[2]/div/div[2]/div/div/div[1]/div/ul/li[1]/div/div/div[3]",
        driver,
    )

    norm_val = used_amount1.text

    next_page = get_element(
        "xpath",
        "/html/body/div[1]/div/div/div[6]/div[3]/div[2]/div/div[2]/span[2]",
        driver,
    )
    next_page.click()

    used_amount2 = get_element(
        "xpath",
        '//*[@id="root"]/div/div/div[6]/div[3]/div[2]/div/div[2]/div/div/div[1]/div/ul/li[2]/div/div/div[3]',
        driver,
    )
    full_val = used_amount2.text

    norm_val = norm_val.split(" ")
    full_val = full_val.split(" ")

    used_stand, used_free = 0, 0

    for i in norm_val:
        try:
            used_stand = float(i)
            break
        except Exception:
            pass

    used_free_temp = 0
    for i in full_val:
        try:
            used_free_temp = float(i)
            break
        except Exception:
            pass

    used_free = used_free_temp - used_stand

    wifi_data = {
        "used_stand": used_stand,
        "used_free": used_free,
    }
    return wifi_data


def get_date() -> dict[str, str | int]:
    today = date.today()
    today = str(today.strftime("%d/%m/%Y"))

    date_list = list(today)

    date_ = int(date_list[0] + date_list[1])
    month = int(date_list[3] + date_list[4])
    year = int(date_list[-4] + date_list[-3] + date_list[-2] + date_list[-1])

    days = 30
    if month in [1, 3, 5, 7, 8, 10, 12]:
        days = 30
    elif month == 2:
        if year % 4 == 0:
            days = 29
        else:
            days = 28
    else:
        days = 30

    data: dict[str, str | int] = {
        "date_str": today,
        "date": date_,
        "month": month,
        "days": days,
    }
    return data


class App(ttk.Window):
    def __init__(
        self,
        title="Terminal Wifi Checker",
        themename="darkly",
        iconphoto=None,
        size=None,
        minsize=None,
        resizable=(False, False),
        date_data=None,
        wifi_data=None,
    ):
        super().__init__(
            title,
            themename,
            iconphoto,
            size,
            minsize,
            resizable=resizable,
        )
        self.date_data = date_data
        self.wifi_data = wifi_data

        self.bind("<Return>", self.quit_app)
        self.bind("<q>", self.quit_app)

        title_frame = ttk.Frame(self)
        title_frame.place(x=0, y=0, relwidth=1, relheight=0.15)

        title_label = ttk.Label(
            title_frame,
            text=f"Terminal Wifi Checker - {self.date_data['date_str']}",
            font=("Arial", 24),
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")

        content_frame = ttk.Frame(self)
        content_frame.place(relx=0, rely=0.15, relheight=0.85, relwidth=1)

        stand_meter_frame = MeterFrame(
            content_frame,
            "Standard\nUsage",
            date_data=self.date_data,
            wifi_data=self.wifi_data,
        )
        stand_meter_frame.place(relx=0, rely=0, relheight=1, relwidth=0.3)

        free_meter_frame = MeterFrame(
            content_frame,
            "Free\nUsage",
            date_data=self.date_data,
            wifi_data=self.wifi_data,
        )
        free_meter_frame.place(
            relx=1, rely=0, relheight=1, relwidth=0.3, anchor="ne"
        )

        self.full_meter = ttk.Meter(
            content_frame,
            metertype="semi",
            amounttotal=100,
            bootstyle="info",
            meterthickness=15,
            stripethickness=5,
            textright="%",
            subtext="Total\nUsed",
        )
        self.full_meter.place(relx=0.3, rely=0, relwidth=0.4, relheight=1)
        self.set_full_meter()

        stand_use_lbl = ttk.Label(
            content_frame,
            text=f"Standard usage: {self.wifi_data['used_stand']:.2f}GB",
            font=("Arial", 16),
        )
        stand_use_lbl.place(relx=0.5, rely=0.6, anchor="center")

        free_use_lbl = ttk.Label(
            content_frame,
            text=f"Free usage: {self.wifi_data['used_free']:.2f}GB",
            font=("Arial", 16),
        )
        free_use_lbl.place(relx=0.5, rely=0.7, anchor="center")

    def set_full_meter(self):
        total_usage = self.wifi_data["used_free"] + self.wifi_data["used_stand"]
        usage_perc = round((total_usage / 100) * 100)
        self.full_meter.amountusedvar.set(usage_perc)

    def quit_app(self, event):
        self.quit()


class MeterFrame(ttk.Frame):
    def __init__(self, master, label_text: str, wifi_data, date_data) -> None:
        super().__init__(master)

        self.wifi_data = wifi_data
        self.date_data = date_data
        self.meter_label = label_text

        self.meter = ttk.Meter(
            self,
            metertype="semi",
            amounttotal=100,
            bootstyle="success",
            meterthickness=15,
            stripethickness=5,
            textright="%",
            subtext=self.meter_label,
        )
        self.meter.place(relx=0.5, rely=0.1, anchor="n")

        self.average_used_lbl = ttk.Label(self, text="Average used: 10000")
        self.average_used_lbl.place(relx=0.5, rely=0.65, anchor="center")

        self.target_average_lbl = ttk.Label(self, text="Target average: 10000")
        self.target_average_lbl.place(relx=0.5, rely=0.72, anchor="center")

        self.available_average_lbl = ttk.Label(
            self, text="Available average: 10000"
        )
        self.available_average_lbl.place(relx=0.5, rely=0.8, anchor="center")

        self.set_values()

    def set_values(self):
        if "free" in self.meter_label.lower():
            values = self.calc_percent(self.wifi_data["used_free"], total=60)

            self.available_average_lbl.configure(
                text=f"Average available: {values['remaining_average']}GB"
            )
            self.average_used_lbl.configure(
                text=f"Average used: {values['average_used']}GB"
            )
            self.target_average_lbl.configure(
                text=f"Target average: {values['typical_usage']}GB"
            )
            self.meter.amountusedvar.set(int(values["usage_percent"]))

            if 95 < values["usage_percent"] < 100:
                self.meter.configure(bootstyle="warning")

            elif values["usage_percent"] >= 100:
                self.meter.configure(bootstyle="danger")

            else:
                self.meter.configure(bootstyle="success")

        else:
            values = self.calc_percent(self.wifi_data["used_stand"], total=40)

            self.available_average_lbl.configure(
                text=f"Average available: {values['remaining_average']}GB"
            )
            self.average_used_lbl.configure(
                text=f"Average used: {values['average_used']}GB"
            )
            self.target_average_lbl.configure(
                text=f"Target average: {values['typical_usage']}GB"
            )
            self.meter.amountusedvar.set(int(values["usage_percent"]))

            if 95 < values["usage_percent"] < 100:
                self.meter.configure(bootstyle="warning")

            elif values["usage_percent"] >= 100:
                self.meter.configure(bootstyle="danger")

            else:
                self.meter.configure(bootstyle="success")

    def calc_percent(self, used, total: int = 40):
        date = self.date_data["date"]
        days = self.date_data["days"]

        typical_usage = round(total / days, 2)
        average_used = round(used / date, 2)
        try:
            remaining_average = round(((total - used) / (days - date)), 2)
        except ZeroDivisionError:
            remaining_average = average_used

        usage_percent = round((used / (typical_usage * date)) * 100)

        return {
            "typical_usage": typical_usage,
            "average_used": average_used,
            "remaining_average": remaining_average,
            "usage_percent": usage_percent,
        }


if __name__ == "__main__":
    main_app()
