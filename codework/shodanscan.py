# will take in the dict from scan query gather and retrurn the output of each query for processing

import shodan


# this should be called right after scan select
def get_api_key():
    """Asks the user for the Shodan API key and returns a valid key."""

    key = input("Enter your Shodan API key: ").strip()

    try:
        # Initialize the client with the provided key
        api = shodan.Shodan(key)

        # .info() returns account details (credits, etc).
        # If the key is bad, this line will crash (raise an exception).
        api.info()

        print("✅ API key is valid.")
        return key

    except shodan.APIError:
        print("❌ Invalid API key. Please check your input.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error validating key: {e}")
        return False


def query_parse(selected_queries: dict, api_key: str) -> dict:
   
