import environ
import requests

env = environ.Env()
environ.Env.read_env()


def get_exchange_rate(currency, date=None):
    if currency == "UAH":
        return 1

    if date:
        url = f"{env('OPEN_EXCHANGE_RATES_URL')}/historical/{date}.json"
    else:
        url = f"{env('OPEN_EXCHANGE_RATES_URL')}/latest.json"

    params = {
        "app_id": env("OPEN_EXCHANGE_RATES_APP_ID"),
        "symbol": f"{currency}, UAH",
    }

    try:
        response = requests.get(
            url, params=params, headers={"accept": "application/json"}
        )
        response.raise_for_status()
        data = response.json()

        if "rates" in data and currency in data["rates"] and "UAH" in data["rates"]:
            return data["rates"]["UAH"] / data["rates"][currency]

    except requests.exceptions.HTTPError as e:
        print(f"Помилка отримання курсу валют: {e}")

    return None
