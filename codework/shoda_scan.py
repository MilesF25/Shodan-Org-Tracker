"""This file is for the scanning of the organizations, I want to try and get as many as possible in one scan or have the user just find it themselves"""

import edit_and_decision_func
import questionary

# plan, 1. look at config for org query to scan
# will again show the orgs and the orgs in it, will ask the user to select
# load config file or go through it

# single scan, mutliple scan, and org scans and everything (maybe)


# 2. use shodan api to scan for the org
# 3. save results to sqlite db
# 4. comparison to see difference since last scan
# will also need to make a function for daily scans, have user set list of what orgs to scan and maybe time. also keep track of api usage


# this function will figure out what the user wants to scan, either they select a single org scan, multiple org scans, or all org scans
def scan_choice():
    decision = questionary.select(
        "Select what kind of scan you'd like to perform:",
        choices=[
            "Single Org Scan",  # will select 1 org to scan and the targets in it (will also be selectable with an all otpion)
            "Multiple Org Scans",
            "All Org Scans",
            "Cancel",
        ],
        qmark="",
    ).ask()
    return decision


def shodan_scans_menu_single(config_data):
    """Menu to manage scan targets for a selected organization."""
    print("Selected Single Org Scan\n")
    # Build a list of organization names from the config for the selection UI
    org_choices = [
        org["name"] for org in config_data["organizations"]
    ]  # list comprehension -> ['Org A', 'Org B', ...]

    # If there are no organizations configured, inform the user and exit
    if not org_choices:
        print("\nPlease add an organization first.")  # user feedback
        return  # no org to manage, so return early

    # Ask the user to pick which organization's scan targets to manage
    selected_org_name = questionary.select(
        "Select what orgs you'd like to scan",  # prompt text
        choices=org_choices,  # choices shown in the select menu
        qmark="",  # visual style configuration
    ).ask()  # .ask() displays the prompt and returns the selected value (or None)

    # If the user cancelled the selection (None), stop here
    if not selected_org_name:
        return

    # Locate the organization dict that matches the selected name
    org_object = next(
        (
            org
            for org in config_data["organizations"]
            if org["name"] == selected_org_name
        ),
        None,  # default if no match found
    )

    # If we couldn't find the organization (shouldn't happen normally), abort
    if not org_object:
        return

    # Display header for the scan target listing
    print(f"\n--- Current Scan Targets for '{selected_org_name}' ---")

    # If the org has no targets configured, print 'None.' otherwise list them
    if not org_object["targets_to_monitor"]:
        print("No targets")  # nothing to show, TODO: add better looping
    else:
        # here is where they can select scan all, select amount or scan 1
        queries = questionary.checkbox(
            "Select which targets to scan:",
            choices=org_object["targets_to_monitor"],
            qmark="",
        ).ask()

    return queries


# here is where the user can select scan all, select amount or scan 1
# first need to iterate through the org targets and show them to the user

# TODO: finsish scan functions, multiple orgs, all orgs and cancle
# TODO: IMplement scanning functions


def main():
    # first will load config
    config_data = edit_and_decision_func.config_opener()
    if not config_data:
        print("Failed to load configuration.")
        return
    # then will go to the scan management menu
    test_list = shodan_scans_menu_single(config_data)
    print(test_list)


main()
