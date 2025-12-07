import os
import json
import re
from difflib import SequenceMatcher
import questionary
from questionary import Style
import scan_query_gather

CONFIG_PATH = "config.json"

# ==============================================================================
# --- Helper Functions (Slightly modified for new structure) ---
# ==============================================================================


# TODO: piviot: the goal is to now have the user enter the orgs and queires for known assets. each asset will have a query that can find it
# if a scan for the org is run, it should find the assets, but if it finds an asset not registered it should alert the user.
# what is in the configi is the konown assets and their queries to find them


# TODO: DB compare should jsut look at the org name and then look at the table for quick look up. if org matches then look at ip to find.
# if ip don't match anything raise flag


def config_opener(config_file: str = CONFIG_PATH) -> dict:
    """Function to open and load the configuration file."""
    # Return a normalized config structure. If the file doesn't exist we return
    # a default structure so callers can operate without special-casing a
    # missing configuration file; callers should call `save_config` when they
    # want to persist changes back to disk.
    if not os.path.exists(config_file):
        print(
            "Welcome. Looks like its your first time here so lets set up a config file. It will be made in the current directory, \n"
        )
        print(
            "Everything in the config file should be a known asset of the organization. \n"
        )
        return {"organizations": []}  # Return a default structure
    try:
        with open(config_file, "r") as f:
            config_data = json.load(f)
            print("Config loaded sucessfully.")
            # Ensure the top-level key exists for compatibility
            if "organizations" not in config_data:
                print(
                    "Hmmmm looks like the config file is missing the 'organizations' key. Initializing it now but you'll have to re-add any orgs you had before."
                )
                config_data = {"organizations": []}
            return config_data
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{config_file}'.")
        return None
    except IOError:
        print(f"Error: Could not read '{config_file}'.")
        return None


def save_config(config_data, config_file: str = CONFIG_PATH):
    """Saves the given data to the config file."""
    # Persist the provided configuration dict to disk. This uses a simple
    # write operation; for stronger guarantees (avoid truncated files on
    # crash), consider writing to a temp file and atomically replacing the
    # original file.
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            # ensure_ascii=False preserves unicode characters nicely in the
            # JSON file so names and non-ASCII chars are readable.
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print("\n[+] Configuration saved successfully.")
    except Exception as e:
        print(f"\n[!] Error saving configuration: {e}")


def normalize_org_name(name: str) -> str:
    """Normalize organization name for comparison."""
    # Create a canonical, comparable version of an org name for equality and
    # fuzzy matching: lowercase, remove punctuation, collapse spaces.
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9 ]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name


def is_probably_duplicate(new_name, existing_orgs_list, threshold=0.80):
    """Checks if a new name is probably a duplicate of an existing one."""
    # Return the first existing org name that is similar enough to the new
    # name according to a SequenceMatcher ratio. Callers may prompt the user
    # when a similar name is found.
    for existing_org in existing_orgs_list:
        score = SequenceMatcher(
            None,
            normalize_org_name(new_name),
            normalize_org_name(existing_org["organization_name"]),
        ).ratio()
        if score >= threshold:
            return existing_org[
                "organization_name"
            ]  # Return the name of the similar org
    return None


# ==============================================================================
# --- Refactored Organization Management ---
# ==============================================================================
def add_org(config_data):
    """Adds a new organization to the config."""
    new_org_name = questionary.text(
        "Enter the new organization's name:",
    ).ask()
    if not new_org_name:
        print("Organization name cannot be empty.")
        return

    # Check for exact duplicates
    if any(
        org["organization_name"].lower() == new_org_name.lower()
        for org in config_data["organizations"]
    ):
        print(f"Organization '{new_org_name}' already exists.")
        return

    # Your fuzzy matching logic
    similar_name = is_probably_duplicate(new_org_name, config_data["organizations"])
    if similar_name:
        if not questionary.confirm(
            f"⚠️ '{new_org_name}' looks similar to '{similar_name}'. Add it anyway?"
        ).ask():
            print("Operation cancelled.")
            return

    new_org_object = {"organization_name": new_org_name, "targets_to_monitor": []}
    config_data["organizations"].append(new_org_object)
    print(f"✅ Added organization: {new_org_name}")
    save_config(config_data)


def remove_org(config_data):
    """Removes an organization from the config."""
    org_choices = [org["organization_name"] for org in config_data["organizations"]]
    if not org_choices:
        print("No organizations to remove.")
        return

    org_to_remove = questionary.select(
        "Which organization to remove?", choices=org_choices
    ).ask()
    if (
        org_to_remove
        and questionary.confirm(f"Remove '{org_to_remove}' and all its scans?").ask()
    ):
        config_data["organizations"] = [
            org
            for org in config_data["organizations"]
            if org["organization_name"] != org_to_remove
        ]
        print(f"🗑️ Removed organization: {org_to_remove}")
        save_config(config_data)


def rename_org(config_data):
    """Renames an organization."""
    org_choices = [org["organization_name"] for org in config_data["organizations"]]
    if not org_choices:
        print("No organizations to rename.")
        return

    org_to_rename = questionary.select(
        "Which organization to rename?", choices=org_choices
    ).ask()
    if not org_to_rename:
        return

    new_name = questionary.text(f"Enter the new name for '{org_to_rename}':").ask()
    if not new_name:
        print("New name cannot be empty.")
        return

    # Check if new name already exists
    if new_name in [o["organization_name"] for o in config_data["organizations"]]:
        print(f"Organization '{new_name}' already exists.")
        return

    for org in config_data["organizations"]:
        if org["organization_name"] == org_to_rename:
            org["organization_name"] = new_name
            print(f"📝 Renamed '{org_to_rename}' → '{new_name}'")
            save_config(config_data)
            return


# ==============================================================================
# --- NEW: Scan Target Management ---
# ==============================================================================
def add_scan_target(org_object):
    """Adds a new scan target to a specific organization."""
    property_name = questionary.text(
        "Enter a descriptive property name for this scan:",
    ).ask()
    target_query = questionary.text(
        f"Enter the full Shodan query for '{property_name}':",
    ).ask()

    if property_name and target_query:
        org_object["targets_to_monitor"].append(
            {"property_name": property_name, "query": target_query}
        )
        print(f"✅ Added target '{property_name}'.")


def remove_scan_target(org_object):
    """Removes a scan target from an organization."""
    target_choices = [t["property_name"] for t in org_object["targets_to_monitor"]]
    if not target_choices:
        print("This organization has no scan targets to remove.")
        return

    property_name = questionary.select(
        "Which scan target to remove?",
        choices=target_choices,
    ).ask()
    if property_name:
        org_object["targets_to_monitor"] = [
            t
            for t in org_object["targets_to_monitor"]
            if t["property_name"] != property_name
        ]
        print(f"🗑️ Removed target '{property_name}'.")


# ==============================================================================
# --- Menu System (Using and Integrating Your Functions) ---
# ==============================================================================
def manage_scans_menu(config_data):
    """Menu to manage scan targets for a selected organization."""
    # Build a list of organization names from the config for the selection UI
    print("Do ctrl+c to exit back to menu\n")
    org_choices = [
        org["organization_name"] for org in config_data["organizations"]
    ]  # list comprehension -> ['Org A', 'Org B', ...]

    # If there are no organizations configured, inform the user and exit
    if not org_choices:
        print("\nPlease add an organization first.")  # user feedback
        return  # no org to manage, so return early

    # Ask the user to pick which organization's scan targets to manage
    selected_org_name = questionary.select(
        "Manage scans for which organization?",  # prompt text
        choices=org_choices,  # choices shown in the select menu
    ).ask()  # .ask() displays the prompt and returns the selected value (or None)

    # If the user cancelled the selection (None), stop here
    if not selected_org_name:
        return

    # Locate the organization dict that matches the selected name
    org_object = next(
        (
            org
            for org in config_data["organizations"]
            if org["organization_name"] == selected_org_name
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
        print("None.")  # nothing to show
    else:
        # Iterate and print each target's user-friendly name and its query
        for target in org_object["targets_to_monitor"]:
            print(f'- {target["property_name"]}: "{target["query"]}"')
    # Print a divider line after the target list
    print("-" * 30)

    # Ask the user whether to add or remove a scan target or go back
    action = questionary.select(
        f"Action for '{selected_org_name}':",  # dynamic prompt showing org name
        choices=["Add Scan Target", "Remove Scan Target", "Back"],
    ).ask()

    # If the user chose to add a scan target, call the add helper and save
    if action == "Add Scan Target":
        add_scan_target(org_object)  # mutate org_object in place
        save_config(config_data)  # persist changes to disk
    # If the user chose to remove a scan target, call the remove helper and save
    elif action == "Remove Scan Target":
        remove_scan_target(org_object)  # mutate org_object in place
        save_config(config_data)  # persist changes to disk


def manage_orgs_menu(config_data):
    """config_options function as a menu router."""
    # Simple router to map a user's selection to the concrete add/remove/rename
    # operations. Each operation mutates `config_data` and persists changes via
    # `save_config` when appropriate.
    action = questionary.select(
        "Organization Management",
        choices=[
            "Add Organization",
            "Remove Organization",
            "Rename Organization",
            "Back",
        ],
    ).ask()

    if action == "Add Organization":
        add_org(config_data)
    elif action == "Remove Organization":
        remove_org(config_data)
    elif action == "Rename Organization":
        rename_org(config_data)


def main():
    """Main application loop, using your original structure."""
    # Basic interactive main loop. This keeps the program running until the
    # user explicitly chooses to exit.
    # will greet here
    # TODO: make config opener a var to pass into funs
    config_file = config_opener()
    while True:
        choice = questionary.select(
            "\nWhat would you like to do?",
            choices=["Scan", "Check DB", "Manage Orgs", "Manage Scans", "Exit"],
            qmark="",
        ).ask()

        if choice == "Scan":
            print("You chose to Scan.")  # Your scanning function would go here
            query_list = scan_query_gather.query_collect()
            # TODO have the scanned queries do something
            # if query_list == None:

            # also in a seperate file
        elif choice == "Check DB":
            print("You chose to Check DB.")  # Your DB checking function here
            # this will be in a seperate fi,e
        elif choice == "Manage Orgs":
            config = config_opener()
            if config:
                manage_orgs_menu(config)
        elif choice == "Manage Scans":
            config = config_opener()
            if config:
                manage_scans_menu(config)
        elif choice == "Exit" or choice is None:
            print("Exiting.")
            break


if __name__ == "__main__":
    main()
