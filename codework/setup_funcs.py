import json
import os
import shodan
import requests


def check_for_config_file() -> bool:
    """Checks if the Shodan config file exists."""

    return os.path.isfile("config.json")


def run_setup_wizard() -> bool:
    """
    Interactively prompts the user for necessary information and creates the config.json file, returns bool.
    """
    print("--- Welcome to the Attack Surface Time Machine Setup --- \n")
    print(
        "It looks like this is your first time running the tool. Let's get configured."
    )
    print(
        "--- Keep in mind this program will encrypt the stored key on start up and decrypt on exit"
    )

    # Prompt for the organization
    target_org = input(
        "Enter the exact organization name to monitor (e.g., 'Google LLC'): "
    )

    # Create the configuration dictionary
    config_data = {"target_organization": [target_org]}

    # Write the data to the config.json file
    try:
        with open("config.json", "w") as f:
            json.dump(config_data, f, indent=4)
        print("\n[+] Configuration saved successfully to config.json!")
        print("    You can run the script again now to perform your first scan.")
        return True
    except Exception as e:
        print(f"\n[!] Error: Could not write to config.json. Details: {e}")
        return False


def get_api_key():
    """Asks the user for the Shodan API key and returns a Shodan API client."""

    key = input("Enter your Shodan API key: ").strip()
    # validate = shodan.Shodan(key)
    # response = requests.get(f"https://api.shodan.io/api-info?key={key}")
    api = shodan.Shodan(key)
    try:
        info = api.info()
        if info:
            print("✅ API key is valid.")
            return key
        else:
            return False
        # if response.status_code == 200:
        #     print("✅ API key is valid.")
        #     return key
        # else:
        #     print("Invalid API key. Try again.")
        #     return False
    except shodan.APIError:
        print("Invalid API key. Try again.")
        return False
    except Exception as e:
        print(f"Error while validating key: {e}")
        return False


import json
import os


def generate_config_interactively():
    """
    An interactive wizard to create a structured config.json file for monitoring.
    """
    print("--- Configuration File Generator ---")
    print("Let's set up the targets you want to monitor.")

    # The main data structure that will be saved to JSON
    final_config = {"organizations": []}

    # --- Outer loop for adding organizations ---
    while True:
        print("\n--- Adding a New Organization ---")
        main_org_name = input(
            "Enter the main organization name (e.g., My University) or press Enter to finish: "
        )
        if not main_org_name:
            break

        # Create the dictionary for this organization
        org_object = {"name": main_org_name, "targets_to_monitor": []}

        # --- Inner loop for adding specific scans (targets) to this organization ---
        while True:
            print(f"\n--- Adding a scan target for '{main_org_name}' ---")

            # Get a descriptive name for this specific scan
            target_name = input(
                "Enter a descriptive name for this scan (e.g., 'Exposed Databases'): "
            )
            if not target_name:
                print("Scan name cannot be empty. Please try again.")
                continue

            # Get the exact Shodan query
            target_query = input(f"Enter the full Shodan query for '{target_name}': ")
            if not target_query:
                print("Shodan query cannot be empty. Please try again.")
                continue

            # Create the dictionary for this specific target
            target_object = {"name": target_name, "query": target_query}

            # Add the new target to the current organization's list
            org_object["targets_to_monitor"].append(target_object)
            print(f"[+] Added target '{target_name}' to '{main_org_name}'.")

            # Ask if the user wants to add another scan FOR THIS SAME ORGANIZATION
            another_scan = (
                input(f"Add another scan for '{main_org_name}'? (y/n): ")
                .lower()
                .strip()
            )
            if another_scan != "y":
                break

        # Add the fully populated organization object to our main list
        final_config["organizations"].append(org_object)

        # Ask if the user wants to add ANOTHER ENTIRE ORGANIZATION
        another_org = (
            input("\nAdd another entire organization to monitor? (y/n): ")
            .lower()
            .strip()
        )
        if another_org != "y":
            break

    # --- Save the final configuration to a file ---
    config_filename = "config.json"
    try:
        with open(config_filename, "w") as f:
            # Use indent=2 for nice, human-readable formatting
            json.dump(final_config, f, indent=2)
        print(
            f"\n[SUCCESS] Configuration has been saved to '{os.path.abspath(config_filename)}'"
        )
    except Exception as e:
        print(f"\n[ERROR] Failed to save configuration file. Details: {e}")


if __name__ == "__main__":
    generate_config_interactively()
