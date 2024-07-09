from dataclasses import dataclass
import requests


WEBSOCKET_URL = "wss://websocket-api.tibber.com/v1-beta/gql/subscriptions"
GRAPHQL_ENDPOINT = "https://api.tibber.com/v1-beta/gql"
# https://developer.tibber.com/settings/access-token
TOKEN = "<TOKEN>"


@dataclass
class Home:
    id: str
    timeZone: str
    address: dict
    features: dict


def gql_request(query):
    response = requests.post(
        GRAPHQL_ENDPOINT,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
        json={"query": query},
    )
    response.raise_for_status()
    return response.json()


def get_home() -> Home:
    query = """
    {
        viewer {
            homes {
                id
                timeZone
                address {
                    address1
                    postalCode
                    city
                }
                features {
                    realTimeConsumptionEnabled
                }
            }
        }
    }
    """
    data = gql_request(query)
    home_data = data["data"]["viewer"]["homes"][0]
    return Home(
        id=home_data["id"],
        timeZone=home_data["timeZone"],
        address=home_data["address"],
        features=home_data["features"],
    )


def get_websocket_url():
    # Not sure what this is needed for. It was in one of the examples.
    query = """
    {
      viewer {
        websocketSubscriptionUrl
      }
    }
    """
    data = gql_request(query)
    url = data["data"]["viewer"]["websocketSubscriptionUrl"]


def subscribe_to_live_measurement(home_id: str):
    # subscription{
    #   liveMeasurement(homeId:"96a14971-525a-4420-aae9-e5aedaa129ff") {
    #     timestamp
    #     power
    #     maxPower
    #   }
    # }
    pass


def get_subscription_info():
    query = """
    {
      viewer {
        homes {
          currentSubscription {
            priceInfo {
              current {
                total
                energy
                tax
                startsAt
              }
            }
          }
        }
      }
    }
    """
    data = gql_request(query)
    return data


def main():
    home = get_home()
    print(home)


if __name__ == "__main__":
    main()
