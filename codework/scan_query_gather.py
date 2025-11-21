import semi_main
import questionary

"""This file is to get figure out what the user wants to scan and returns the queries in list"""
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


# let ai auto completes, hopefully it works hah
def shodan_all_org_scans(config_data):
    """Function to scan all orgs in the config file"""
    print("Selected All Org Scans\n")
    queries_to_process = []

    for org in config_data["organizations"]:
        targets = org.get("targets_to_monitor") or []
        if not targets:
            print(f"No targets defined for '{org['name']}'.")
            continue

        for t in targets:
            q = t.get("query")
            if q:
                queries_to_process.append(q)

    print(f"\nCollected {len(queries_to_process)} queries from all orgs.")
    return queries_to_process


# let ai improve
def shodan_scans_menu_multiple(config_data):
    """Menu to manage scan targets for a selected organization."""
    # Informational header
    print("Selected Multiple Org Scan\n")
    # Build a list of organization names from the config for the selection UI
    org_choices = [
        org["name"] for org in config_data["organizations"]
    ]  # list comprehension -> ['Org A', 'Org B', ...]

    # If there are no organizations configured, inform the user and exit
    if not org_choices:
        print("\nPlease add an organization first.")  # user feedback
        return  # no org to manage, so return early

    # Ask the user to pick which organization's scan targets to manage
    selected_org_name = questionary.checkbox(
        "Select what orgs you'd like to scan",  # prompt text
        choices=org_choices,  # choices shown in the select menu
        qmark="",  # visual style configuration
    ).ask()  #
    # If the user cancelled the selection (None) or selected none, return an empty list
    if not selected_org_name:
        return print("No orgs selected or user cancelled.")

    # Collect all queries from the selected organizations' targets
    queries_to_process = []

    for org_name in selected_org_name:
        # Find the organization object by name
        org_object = next(
            (org for org in config_data["organizations"] if org["name"] == org_name),
            None,
        )

        if not org_object:
            # Shouldn't happen, but skip if no match
            print(f"Warning: organization '{org_name}' not found in config.")
            continue

        # If the org has no targets configured, skip with a friendly message
        targets = org_object.get("targets_to_monitor") or []
        if not targets:
            print(f"No targets defined for '{org_name}'.")
            continue

        # Extend the queries list with each target's 'query' value
        for t in targets:
            q = t.get("query")
            if q:
                queries_to_process.append(q)

    # Optionally show a brief summary to the user
    print(
        f"\nCollected {len(queries_to_process)} queries from {len(selected_org_name)} org(s)."
    )

    # Return the list of query strings for processing later
    return queries_to_process


# my original version
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
        # Set to none if there are no queires
        queries = None

    else:
        # here is where they can select scan all, select amount or scan 1
        queries = questionary.checkbox(
            "Select which targets to scan:",
            choices=org_object["targets_to_monitor"],
            qmark="",
        ).ask()
    if queries == None:
        print(
            "You're seeing this because there are probably no queries in the selected organization(s). Go back and add some"
        )
    else:
        return queries


def main():
    """This function will return the queires for all the orgs in a list"""
    # first will load config
    config_data = semi_main.config_opener()
    if not config_data:
        print("Failed to load configuration.")
        return
    # then will go to the scan management menu
    decision = scan_choice()
    if decision == "Single Org Scan":
        query_list = shodan_scans_menu_single(config_data)
    elif decision == "Multiple Org Scans":
        query_list = shodan_scans_menu_multiple(config_data)
    elif decision == "All Org Scans":
        print(
            "You will be scanning every organization and its queiries. Make sure to check if you have the resources to!"
        )
        query_list = shodan_all_org_scans(config_data)
    else:
        print("scan cancelled")

        # if query_list == None:
        #     print(
        #         "You're seeing this because there are probably no queries in the selected organization(s). Go back and add some"
        #     )
        # else:
        # need to handle if query is empty
    return print(query_list)


main()
