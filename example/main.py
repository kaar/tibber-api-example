from dataclasses import dataclass
import asyncio
import json
import requests

# https://github.com/Danielhiversen/pyTibber
from gql.transport.websockets import WebsocketsTransport
from gql import gql, Client


WEBSOCKET_URL = "wss://websocket-api.tibber.com/v1-beta/gql/subscriptions"
GRAPHQL_ENDPOINT = "https://api.tibber.com/v1-beta/gql"
# https://developer.tibber.com/settings/access-token
TOKEN = "<TOKEN>"


@dataclass
class Home:
    """
    Example:
    {
      "id": "0f0d73e7-387f-410e-9bef-f609aff70ec9",
      "timeZone": "Europe/Stockholm",
      "address": {
        "address1": "Str\u00f6mshammar 1",
        "postalCode": "64296",
        "city": "Malmk\u00f6ping"
      },
      "features": {
        "realTimeConsumptionEnabled": false
      },
      "currentSubscription": {
        "priceInfo": {
          "current": {
            "total": 0.5101,
            "energy": 0.3281,
            "tax": 0.182,
            "startsAt": "2024-07-09T12:00:00.000+02:00"
          }
        }
      }
    }
    """

    id: str
    timeZone: str
    address: dict
    features: dict
    currentSubscription: dict

    def __str__(self):
        # Print it as JSON
        return json.dumps(self.__dict__, indent=2)


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
    home_data = data["data"]["viewer"]["homes"][0]
    return Home(
        id=home_data["id"],
        timeZone=home_data["timeZone"],
        address=home_data["address"],
        features=home_data["features"],
        currentSubscription=home_data["currentSubscription"],
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


async def realtime_measurments(home_id: str):
    query = """
        subscription {
            liveMeasurement(homeId:"%s"){
                accumulatedConsumption
                accumulatedConsumptionLastHour
                accumulatedCost
                accumulatedProduction
                accumulatedProductionLastHour
                accumulatedReward
                averagePower
                currency
                currentL1
                currentL2
                currentL3
                lastMeterConsumption
                lastMeterProduction
                maxPower
                minPower
                power
                powerFactor
                powerProduction
                powerReactive
                signalStrength
                timestamp
                voltagePhase1
                voltagePhase2
                voltagePhase3
            }
        }
    """
    transport = WebsocketsTransport(
        url=WEBSOCKET_URL,
        init_payload={"token": TOKEN},
    )
    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:
        async for data in session.subscribe(gql(query % home_id)):
            print(data)
            """
            I get the following exception:
                gql.transport.exceptions.TransportQueryError:
                {'message': 'No live measurements available for this home 0f0d73e7-387f-410e-9bef-f609aff70ec9 user agent Python/3.12 websockets/11.0.3.
                You need to have a tibber pulse device paired for this feature to be available',

            It probably because I don't have anything streaming.
            """


async def main():
    home = get_home()
    print(home)
    await realtime_measurments(home.id)


if __name__ == "__main__":
    asyncio.run(main())
