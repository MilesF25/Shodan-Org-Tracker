"""This file is for the scanning of the organizations, I want to try and get as many as possible in one scan or have the user just find it themselves"""

import edit_and_decision_func

# plan, 1. look at config for org query to scan
# will again show the orgs and the orgs in it, will ask the user to select
# load config file or go through it

# single scan, mutliple scan, and org scans and everything (maybe)

# 2. use shodan api to scan for the org
# 3. save results to sqlite db
# 4. comparison to see difference since last scan
# will also need to make a function for daily scans, have user set list of what orgs to scan and maybe time. also keep track of api usage


def main():
    # first will load config
    config_data = edit_and_decision_func.load_config_file()
    if not config_data:
        print("Failed to load configuration. Exiting.")
        return
    # then will go to the scan management menu
    edit_and_decision_func.manage_scans_menu(config_data)


main()
