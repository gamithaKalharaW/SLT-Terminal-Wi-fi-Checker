from os import getenv
from pathlib import Path

import click
from dotenv import dotenv_values

from wifi_checker import term_main as check_wifi


@click.command()
def main():
    profile_path = Path(getenv("HOMEPATH")).resolve() / ".pywich"
    if profile_path.exists():
        print("Profile config found")
        values = dotenv_values(profile_path)
        print(values)
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
    main()
