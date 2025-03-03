import requests
from datetime import datetime, timedelta

NBU_API_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"


def get_exchange_rate(currency, date=None):
    """
    Отримує курс обміну для вказаної валюти відносно гривні (UAH) з НБУ.

    :param currency: Код валюти (наприклад, "USD", "EUR").
    :param date: (Optional) Дата у форматі YYYY-MM-DD. Якщо None або майбутня дата, бере останній доступний курс.
    :return: Курс обміну або None, якщо валюта не знайдена.
    """
    if currency == "UAH":
        return 1  # Гривня до гривні = 1

    today = datetime.today().strftime("%Y-%m-%d")

    # Якщо дата майбутня → замінюємо її на останній доступний курс (за вчора)
    if date and date > today:
        print(f"⚠️ Дата {date} у майбутньому. Беремо останній доступний курс.")
        date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Формуємо URL для API НБУ
    if date and date < today:
        url = f"{NBU_API_URL}&date={date.replace('-', '')}"
    else:
        url = NBU_API_URL  # Останній доступний курс

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Шукаємо валюту у відповіді API
        for entry in data:
            if entry["cc"] == currency:
                return entry["rate"]

        print(f"❌ Валюта {currency} не знайдена у відповіді API.")

        # Якщо немає курсу за конкретну дату, пробуємо знайти останній доступний
        if date < today:
            last_available_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            print(f"⚠️ Курс на {date} недоступний, пробуємо {last_available_date}")
            return get_exchange_rate(currency, last_available_date)

        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Помилка отримання курсу валют: {e}")
        return None
