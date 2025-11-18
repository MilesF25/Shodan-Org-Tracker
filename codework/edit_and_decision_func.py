# import questionary
# import os
# import json
# import re
# from difflib import SequenceMatcher


# def decision_func() -> str:
#     """Function to decide the next action based on user input."""
#     choice = questionary.select(
#         "What would you like to do", choices=["Scan", "Check DB", "Edit Orgs"]
#     ).ask()

#     return choice


# def selection_tree(user_choice: str):
#     """Function to direct the flow based on user choice."""
#     if user_choice == "Scan":
#         print("You chose to Scan.")
#         # Call the scanning function here
#     elif user_choice == "Check DB":
#         print("You chose to Check DB.")
#         # Call the database checking function here
#     elif user_choice == "Edit Orgs":
#         print("You chose to Edit Orgs.")
#         # Call the organization editing function here
#     else:
#         print("Invalid choice. Please select a valid option.")


# def config_options():
#     """Function to provide configuration options to the user."""
#     choice = questionary.select(
#         "Configuration Options",
#         choices=["Add Organization", "Remove Organization", "Edit Organization Name"],
#     ).ask()

#     return choice


# def config_opener(config_file: str = "config.json") -> dict:
#     """Function to open and load the configuration file."""
#     if not os.path.exists(config_file):
#         print(f"Error: Configuration file not found at '{config_file}'")
#         return None

#     try:
#         with open(config_file, "r") as f:
#             config_data = json.load(f)
#         return config_data
#     except json.JSONDecodeError as e:
#         print(f"Error: Invalid JSON format in '{config_file}': {e}")
#         return None
#     except IOError as e:
#         print(f"Error: Could not read configuration file '{config_file}': {e}")
#         return None
#     except Exception as e:
#         print(f"An unexpected error occurred while loading '{config_file}': {e}")
#         return None


# # will run if use chooses to edit orgs (Could be split into different functions buuuuuuut..... nah)
# def edit_organization(action: str):
#     """Function to edit organizations based on user action."""

#     config = config_opener()  # Load config ONCE
#     if config is None:
#         return  # Stop if config failed to load

#     orgs = config.get("target_organization", [])

#     # ADD
#     if action == "Add Organization":
#         org_name = questionary.text("Enter the organization name to add:").ask()

#         if org_name in orgs:
#             print(f"Organization '{org_name}' already exists.")
#             return

#         orgs.append(org_name)
#         print(f"Added organization: {org_name}")

#     # REMOVE
#     elif action == "Remove Organization":
#         org_name = questionary.text("Enter the organization name to remove:").ask()

#         if org_name not in orgs:
#             print(f"Organization '{org_name}' does not exist.")
#             return

#         orgs.remove(org_name)
#         print(f"Removed organization: {org_name}")

#     # EDIT NAME
#     elif action == "Edit Organization Name":
#         old_name = questionary.text("Enter the current organization name:").ask()

#         if old_name not in orgs:
#             print(f"Organization '{old_name}' does not exist.")
#             return

#         new_name = questionary.text("Enter the new organization name:").ask()

#         if new_name in orgs:
#             print(f"Organization '{new_name}' already exists.")
#             return

#         index = orgs.index(old_name)
#         orgs[index] = new_name

#         print(f"Renamed '{old_name}' → '{new_name}'")

#     else:
#         print("Invalid action.")
#         return

#     # SAVE CHANGES BACK TO FILE (only one place to dump!)
#     with open("config.json", "w") as f:
#         json.dump(config, f, indent=4)

#     print("Config updated successfully.")


# #######################################################################


# # config edit s ection logic


# # gpt did these 2


# def normalize_org_name(name: str) -> str:
#     """Normalize organization name for comparison."""
#     name = name.lower().strip()
#     name = re.sub(r"[^a-z0-9 ]", "", name)  # keep alphanumerics + space
#     name = re.sub(r"\s+", " ", name)  # collapse multiple spaces
#     return name


# def is_probably_duplicate(new, existing, threshold=0.80):
#     """Return True if names are similar based on ratio score."""
#     new_norm = normalize_org_name(new)
#     existing_norm = normalize_org_name(existing)
#     score = SequenceMatcher(None, new_norm, existing_norm).ratio()
#     return score >= threshold


# def check_config() -> bool:
#     """Checks if config is real."""
#     # we assume config file is in the same dir
#     config_path = "config.json"
#     if os.path.exists(config_path):
#         return True

#     else:
#         print(
#             "It looks like the config file does not exist. Check the directory for it. If not, close the program and run the setup wizard."
#         )
#     return False


# def add_organization(new_org: str, config_path: str = "config.json"):
#     # Load config dictionary
#     if os.path.exists(config_path):
#         with open(config_path, "r") as f:
#             config = json.load(f)

#     else:
#         print(
#             "Config file not found. Cannot add organization. Try rerunning the setup."
#         )

#     orgs = config.get("target_organization", [])
#     print(orgs)
#     config["target_organization"] = orgs

#     # Check for similar names before adding
#     for existing in orgs:
#         if is_probably_duplicate(new_org, existing):
#             answer = (
#                 input(
#                     f"⚠️ '{new_org}' looks similar to '{existing}'. "
#                     "Did you mean that one? (y/n): "
#                 )
#                 .strip()
#                 .lower()
#             )

#             if answer in ("y", "yes"):
#                 print(
#                     f"✅ Not Adding {new_org}. Using existing organization: {existing}"
#                 )
#                 return  # Do NOT add
#             elif answer in ("n", "no"):
#                 print("✅ Adding as a new organization.")

#                 break
#             else:
#                 print("Invalid input. Please enter 'y' or 'n'.")
#                 return

#     # Actual append AFTER validation
#     if new_org not in orgs:
#         orgs.append(new_org)
#         print(f"✅ Added organization: {new_org}")
#     else:
#         print(f" '{new_org}' already exists.")

#     # Save to file
#     with open(config_path, "w") as f:
#         json.dump(config, f, indent=4)

#     # Add logic to add the organization to config


# # todo, add remove orgraniztion
# # figure out what to do with api key. rn the program makes a new config if there is no exsiting one.
# # move api key asking to scan part

import os
import json
import re
from difflib import SequenceMatcher
import questionary
from questionary import Style

CONFIG_PATH = "config.json"

# Module: edit_and_decision_func
# Purpose: Interactive helpers for organization and scan management.
#
# This module centralizes small, interactive utilities used by the orgscan
# application. It focuses on reading/writing a JSON config file (default
# `config.json`), managing a list of organizations, and managing scan targets
# associated with each organization. The UI uses `questionary` prompts to keep
# interactions simple and testable.


# To completely REMOVE the question mark, DOES NOT SEEM TO WORK BUT WILL LEAVE HERE CUASE THERE IS NO ISSUE IT SEEMS
style_without_questionmark = Style(
    [
        ("questionmark", ""),  # <-- Set the question mark to an empty string
        ("question", "bold"),
        ("selected", "fg:#5f819d"),
        ("pointer", "fg:#5f819d bold"),
        ("answer", "fg:#5f819d bold"),
    ]
)
# ==============================================================================
# --- Helper Functions (Slightly modified for new structure) ---
# ==============================================================================


def config_opener(config_file: str = CONFIG_PATH) -> dict:
    """Function to open and load the configuration file."""
    # Return a normalized config structure. If the file doesn't exist we return
    # a default structure so callers can operate without special-casing a
    # missing configuration file; callers should call `save_config` when they
    # want to persist changes back to disk.
    if not os.path.exists(config_file):
        print(
            "Welcome. Looks like its your first time here so lets set up a config file. It will be made in the current directory,  \n"
        )
        return {"organizations": []}  # Return a default structure

    try:
        with open(config_file, "r") as f:
            config_data = json.load(f)
            print("Config loaded sucessfully.")
        # Ensure the top-level key exists for compatibility
        if "organizations" not in config_data:
            "Hmmmm looks like the config file is missing the 'organizations' key. Initializing it now but you'll have to re-add any orgs you had before."
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
            None, normalize_org_name(new_name), normalize_org_name(existing_org["name"])
        ).ratio()
        if score >= threshold:
            return existing_org["name"]  # Return the name of the similar org
    return None


# ==============================================================================
# --- Refactored Organization Management ---
# ==============================================================================


def add_org(config_data):
    """Adds a new organization to the config."""
    new_org_name = questionary.text(
        "Enter the new organization's name:", style=style_without_questionmark
    ).ask()
    if not new_org_name:
        print("Organization name cannot be empty.")
        return

    # Check for exact duplicates
    if any(
        org["name"].lower() == new_org_name.lower()
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

    new_org_object = {"name": new_org_name, "targets_to_monitor": []}
    config_data["organizations"].append(new_org_object)
    print(f"✅ Added organization: {new_org_name}")
    save_config(config_data)


def remove_org(config_data):
    """Removes an organization from the config."""
    org_choices = [org["name"] for org in config_data["organizations"]]
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
            org for org in config_data["organizations"] if org["name"] != org_to_remove
        ]
        print(f"🗑️ Removed organization: {org_to_remove}")
        save_config(config_data)


def rename_org(config_data):
    """Renames an organization."""
    org_choices = [org["name"] for org in config_data["organizations"]]
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

    for org in config_data["organizations"]:
        if new_name in [o["name"] for o in config_data["organizations"]]:
            print(f"Organization '{new_name}' already exists.")
            return
        if org["name"] == org_to_rename:
            org["name"] = new_name
            print(f"📝 Renamed '{org_to_rename}' → '{new_name}'")
            save_config(config_data)
            return


# ==============================================================================
# --- NEW: Scan Target Management ---
# ==============================================================================


def add_scan_target(org_object):
    """Adds a new scan target to a specific organization."""
    target_name = questionary.text(
        "Enter a descriptive name for this scan:", style=style_without_questionmark
    ).ask()
    target_query = questionary.text(
        f"Enter the full Shodan query for '{target_name}':",
        style=style_without_questionmark,
    ).ask()
    if target_name and target_query:
        org_object["targets_to_monitor"].append(
            {"name": target_name, "query": target_query}
        )
        print(f"✅ Added target '{target_name}'.")


def remove_scan_target(org_object):
    """Removes a scan target from an organization."""
    target_choices = [t["name"] for t in org_object["targets_to_monitor"]]
    if not target_choices:
        print("This organization has no scan targets to remove.")
        return
    target_name = questionary.select(
        "Which scan target to remove?",
        choices=target_choices,
        style=style_without_questionmark,
    ).ask()
    if target_name:
        org_object["targets_to_monitor"] = [
            t for t in org_object["targets_to_monitor"] if t["name"] != target_name
        ]
        print(f"🗑️ Removed target '{target_name}'.")


# ==============================================================================
# --- Menu System (Using and Integrating Your Functions) ---
# ==============================================================================


def manage_scans_menu(config_data):
    """Menu to manage scan targets for a selected organization."""
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
        "Manage scans for which organization?",  # prompt text
        choices=org_choices,  # choices shown in the select menu
        style=style_without_questionmark,  # visual style configuration
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
        print("None.")  # nothing to show
    else:
        # Iterate and print each target's user-friendly name and its query
        for target in org_object["targets_to_monitor"]:
            print(f'- {target["name"]}: "{target["query"]}"')

    # Print a divider line after the target list
    print("-" * 30)

    # Ask the user whether to add or remove a scan target or go back
    action = questionary.select(
        f"Action for '{selected_org_name}':",  # dynamic prompt showing org name
        choices=["Add Scan Target", "Remove Scan Target", "Back"],
        style=style_without_questionmark,
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
        style=style_without_questionmark,
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
    while True:
        choice = questionary.select(
            "\nWhat would you like to do?",
            choices=["Scan", "Check DB", "Manage Orgs", "Manage Scans", "Exit"],
            style=style_without_questionmark,
        ).ask()

        if choice == "Scan":
            print("You chose to Scan.")  # Your scanning function would go here
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
