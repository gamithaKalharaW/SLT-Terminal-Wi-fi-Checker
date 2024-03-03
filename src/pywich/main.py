from os import getenv
from pathlib import Path

import click
from dotenv import dotenv_values

from .wifi_checker import term_main as check_wifi

# NOTE: to be synced with pyproject.toml version field
VERSION = "0.1.1"

HELP = """
===== PyWiCh ===== 
This is a terminal application meant to be used with MySLT portal
The following options are implemented:
    --help       Show this help message
    --version    Show application version
"""


@click.option("--version", is_flag=True)
@click.option("--help", is_flag=True)
@click.command()
def main_app(version, help):
    if version:
        print(VERSION)
        exit(0)
    if help:
        print(HELP)
        exit(0)
    profile_path = Path(getenv("HOMEPATH")).resolve() / ".pywich"
    if profile_path.exists():
        print("Profile config found")
        values = dotenv_values(profile_path)
        username: str = values["NAME"]
        password: str = values["PASSWORD"]
        check_wifi(username, password)

    else:
        print("Profile config not found")
        print("Creating profile config")
        profile_path.touch()
        name = input("Enter username: ")
        password = input("Enter password: ")
        write_string = f"NAME={name}\nPASSWORD={password}"
        profile_path.write_text(write_string)
        print("Profile created, re-run command to execute")


if __name__ == "__main__":
    main_app()
