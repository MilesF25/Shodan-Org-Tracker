import semi_main
import questionary

# had ai add comments
# goal
"""
    Build a structured list of organizations with their queries.

    Returns:
        List of dicts with format:
        [
            {
                'org_name': 'Example Org',
                'queries': [
                    {'query': 'ssl:"example.com"'},
                    {'query': 'org:"Example Inc"'
                ]
            },
            ...
        ]
        """


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


# thif function is for selecting all the orgs and getting their queries. it will return a dict with the org and all of its orgs and queries


def all_scan(
    config_file,
) -> list:  # this will return a list wiht all the names of the orgs to get queries for.
    # will get the names of the orgs from a the config file
    print("Selected All Org Scans\n")
    org_names = [
        org.get("organization_name") for org in config_file.get("organizations", [])
    ]
    return org_names


def multiple_scans(config_file) -> list:
    """Menu to manage scan targets for a selected organization."""
    # Informational header

    # Build a list of organization names from the config for the selection UI
    org_choices = [
        org["organization_name"] for org in config_file["organizations"]
    ]  # list comprehension -> ['Org A', 'Org B', ...]

    # If there are no organizations configured, inform the user and exit
    if not org_choices:
        print("\nPlease add an organization first.")  # user feedback
        return []  # no org to manage, so return early

    # Ask the user to pick which organization's scan targets to manage
    selected_org_names = questionary.checkbox(
        "Select what orgs you'd like to scan:",
        choices=org_choices,
        qmark="",  # removes question mark
    ).ask()

    if selected_org_names is None:
        print(
            "Looks like there isn't anything selected, make sure you used the spacebar to select the orgs. Make sure to check config file to verify there are orgs in there. OR user quit"
        )
        return []

    return selected_org_names


def single_scan(config_file):
    """Menu to manage scan targets for a selected organization."""
    print("Selected Single Org Scan\n")
    # Build a list of organization names from the config for the selection UI
    org_choices = [
        org["organization_name"]
        for org in config_file["organizations"]
        # org["name"] for org in config_file["organizations"]
    ]  # list comprehension -> ['Org A', 'Org B', ...]

    # If there are no organizations configured, inform the user and exit
    if not org_choices:
        print("\nPlease add an organization first.")  # user feedback
        return  # no org to manage, so return early
    try:
        # Ask the user to pick which organization's scan targets to manage
        selected_org_name = questionary.select(
            "Select what orgs you'd like to scan",  # prompt text
            choices=org_choices,  # choices shown in the select menu
            qmark="",  # visual style configuration
        ).ask()  # .ask() displays the prompt and returns the selected value (or None)

        if selected_org_name is None:
            print(
                "Looks like there isn't anything selected, double check the config file to make sure there are orgs in there. OR user quit"
            )
            return []
        # added just for check
        # print(type(selected_org_name))
    except Exception as e:
        print(f"An error occurred during selection: {e}")
        return []
    # needs to be a list becuase the other functions expect a list, if not it iterates through each character
    return [selected_org_name]


def query_structure(org_names: list, config_file: dict) -> dict:
    """
    Transforms organization data into a structured query format.

    Args:
        org_names: List of organization names to process
        config_file: Configuration dictionary containing organizations

    Returns:
        Dict with format:
        {
            'Example Org': {
                'queries': [
                    {'query': 'ssl:"example.com"'},
                    {'query': 'org:"Example Inc"'}
                ]
            },
            ...
        }
    """
    result = {}

    for org_name in org_names:
        # Find the organization object
        org_object = next(
            (
                org
                for org in config_file["organizations"]
                if org["organization_name"] == org_name
            ),
            None,
        )

        if not org_object:
            print(f"Warning: organization '{org_name}' not found in config.")
            continue

        # Get targets for this org
        targets = org_object.get("targets_to_monitor") or []
        if not targets:
            print(f"No targets defined for '{org_name}'. Skipping.")
            continue

        # Build the queries list from targets
        queries = [{"query": target["query"]} for target in targets]

        # Add to result dict using org name as key
        result[org_object["organization_name"]] = {"queries": queries}

    return result


def query_collect():
    """This function will return the queires for all the orgs in a list"""
    # first will load config
    config_data = semi_main.config_opener()
    if not config_data:
        print("Failed to load configuration.")
        return
    # then will go to the scan management menu
    decision = scan_choice()
    if decision == "Single Org Scan":
        query_list = single_scan(config_data)
    elif decision == "Multiple Org Scans":
        query_list = multiple_scans(config_data)
    elif decision == "All Org Scans":
        print(
            "You will be scanning every organization and its queiries. Make sure to check if you have the resources to!"
        )
        check = input("Are you sure you want to continue? (y/n): ")
        if check.lower() == "y":
            query_list = all_scan(config_data)

    else:
        print("scan cancelled")

        # if query_list == None:
        #     print(
        #         "You're seeing this because there are probably no queries in the selected organization(s). Go back and add some"
        #     )
        # else:
        # need to handle if query is empty
    if not query_list:
        print(
            "Looks like there isn't anything selected, double check the config file to make sure there are orgs in there and run the program again. OR there is another issue tbd"
        )
        return
    query_dict = query_structure(query_list, config_data)
    return query_dict
    # return print(f"this is !!!!!! {query_dict}")


# TODO check the other queires functions and see if they need to be updated to match this new strucutre
