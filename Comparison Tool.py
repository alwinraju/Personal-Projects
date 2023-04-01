""" Script compares bus prices from different providers and outputs the results in a table."""

import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
import streamlit as st
import creds


# INPUT_FROM = input("Depart from: ")
# INPUT_TO = input("Destination: ")
# INPUT_DATE = input("Departure Date (dd/mm/yyyy): ")
# INPUT_TIME = input("Departure Time (hh:mm): ")
# Formatted_date = datetime.strptime(
# INPUT_DATE, "%d/%m/%Y").strftime("%Y-%m-%d")

st.title("Compare UK Intercity Bus Prices")
tab1, tab2 = st.tabs(["Comparison Tool", "Data Analysis"])
tab2.title("Data Analysis")
cities = ["Bristol", "London", "Cardiff"]

# Create dropdown fields for departure and destination
INPUT_FROM = st.selectbox("From", cities)
INPUT_TO = st.selectbox("To", cities, index=1)

# Create input field for departure date
streamlit_date = st.date_input(
    "Departure Date", datetime.now(), min_value=datetime.now()
)
# Convert date to string in format dd/mm/yyyy
INPUT_DATE = datetime.strptime(str(streamlit_date), "%Y-%m-%d").strftime("%d/%m/%Y")

# Create an input field for depart after time, make it default to now and force it to be in the format hh:mm
INPUT_TIME = st.time_input("Depart After", datetime.now()).strftime("%H:%M")

# Create input fields for number of passengers
INPUT_TOTAL_PASSENGERS = st.number_input(
    "Number of Adults", min_value=1, max_value=10, step=1, value=1
)

INPUT_COACH_CARD = st.number_input(
    "National Express Coach Card Passengers", min_value=0, max_value=10, step=1, value=1
)

INPUT_NUS_CARD = st.number_input(
    "NUS Card Passengers", min_value=0, max_value=10, step=1, value=1
)

# Create button to initiate price comparison
if st.button("Compare Prices"):
    # INPUT_FROM = "Bristol"
    # INPUT_TO = "London"
    # INPUT_DATE = "01/04/2023"
    # INPUT_TIME = "17:00"  # This only filters time for national express buses
    Formatted_date = datetime.strptime(INPUT_DATE, "%d/%m/%Y").strftime("%Y-%m-%d")

    provider_list = []
    origin_list = []
    destination_list = []
    date_list = []
    departure_list = []
    arrival_list = []
    duration_list = []
    price_list = []

    # NATIONAL EXPRESS

    NATIONAL_EXPRESS_URL = "https://book.nationalexpress.com/nxrest/journey/search/OUT"
    NationalExpress_Dictionary = {
        "Bristol": 41000,
        "UWE": 41000,
        "London": 57000,
        "Cardiff": 15035,
    }
    NationalExpressData = {
        "coachCard": False,
        "campaignId": "DEFAULT",
        "partnerId": "NX",
        "outboundArriveByOrDepartAfter": "DEPART_AFTER",
        "inboundArriveByOrDepartAfter": "DEPART_AFTER",
        "journeyType": "RETURN",
        "operatorType": "DOMESTIC",
        "leaveDateTime": {"date": (INPUT_DATE), "time": (INPUT_TIME)},
        "passengerNumbers": {
            "numberOfAdults": INPUT_TOTAL_PASSENGERS,
            "numberOfBabies": 0,
            "numberOfChildren": 0,
            "numberOfDisabled": 0,
            "numberOfSeniors": 0,
            "numberOfEuroAdults": 0,
            "numberOfEuroSeniors": 0,
            "numberOfEuroYoungPersons": 0,
            "numberOfEuroChildren": 0,
        },
        "coachCardNumbers": {
            "numberOnDisabledCoachcard": 0,
            "numberOnSeniorCoachcard": 0,
            "numberOnYouthCoachcard": INPUT_COACH_CARD,
        },
        "returnDateTime": {"date": "31/07/2022", "time": "00:00"},
        "fromToStation": {
            "fromStationId": (NationalExpress_Dictionary.get(INPUT_FROM)),
            "toStationId": (NationalExpress_Dictionary.get(INPUT_TO)),
        },
        "onDemand": False,
        "languageCode": "en",
        "channelsKey": "DESKTOP",
    }
    USER_AGENT_LIST = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 13_0_0; en-US; Valve Steam GameOverlay/1676336721; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 13_2_1; en-US; Valve Steam Tenfoot/1676336721; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 13_2_0; en-US; Valve Steam GameOverlay/1675222618; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 13_2_0; en-US; Valve Steam GameOverlay/1675222618; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/420.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 13_1_0; en-US; Valve Steam Tenfoot/1674790765; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 13_0_1; en-US; Valve Steam GameOverlay/1671236931; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 13_1_0; en-US; Valve Steam GameOverlay/1671236931; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 13_0_0; en-US; Valve Steam GameOverlay/1666144119; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:43.0) Gecko/20100101 Firefox/43.0 SeaMonkey/8650",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; rv:31.0) Gecko/20100101 Firefox/30.0 TenFourFox/7477",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR12; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR14; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; rv:17.0) Gecko/17.0 Firefox/17.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; rv:38.0) Gecko/20100101 Firefox/38.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR21; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR30; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR27; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; rv:17.0) Gecko/20130328 Firefox/17.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; rv:31.0) Gecko/20100101 Firefox/31.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; rv:17.0) Gecko/20130105 Firefox/17.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR2; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; rv:17.0) Gecko/20130328 Firefox/17.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; rv:10.0.9) Gecko/20121011 Firefox/10.0.9 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR16; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450 AlexaToolbar/alxf-2.21",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR8; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; rv:10.0.6) Gecko/20120714 Firefox/10.0.6 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR6; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR10; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR7; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR22; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; rv:17.0) Gecko/20130805 Firefox/17.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR12; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR8; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR23; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; rv:17.0) Gecko/20131114 Firefox/17.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.6; FPR31; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR18; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR8; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450 AlexaToolbar/alxf-2.21",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR23; rv:45.0) Gecko/20100101 SVT/1.0.1 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; rv:38.0) Gecko/20100101 Firefox/38.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR32; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR17; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR4; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR3; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR7; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR21; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.5; FPR32; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; rv:17.0) Gecko/20130308 Firefox/17.0 TenFourFox/7450",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X 10.4; FPR6; rv:45.0) Gecko/20100101 Firefox/45.0 TenFourFox/7450",
    ]
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://book.nationalexpress.com",
        "Content-Type": "application/json",
        "Cookie": creds.NX_COOKIE,
        "Content-Length": "795",
        "Accept-Language": "en-GB,en;q=0.9",
        "Host": "book.nationalexpress.com",
        # Select a random user agent from user agent list
        "User-Agent": random.choice(USER_AGENT_LIST),
        "Referer": "https://book.nationalexpress.com/coach/",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

    page = requests.post(
        NATIONAL_EXPRESS_URL,
        headers=headers,
        data=json.dumps(NationalExpressData),
        timeout=60,
    )
    soup = str(BeautifulSoup(page.content, "html.parser"))
    parsed = json.loads(soup)

    def ms_to_hours(millis):
        """Converts milliseconds to hours and minutes."""
        seconds, _ = divmod(millis, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "%dh %dm" % (hours, minutes)

    number_of_tickets = len(parsed["journeyCommand"])
    i = 0
    while i < number_of_tickets:
        provider = "\U000026AA"
        provider_list.append(provider)

        origin = parsed["journeyCommand"][i]["departureStop"]
        if origin == "University of the West of England":
            origin = "Bristol UWE"
            origin_list.append(origin)
        elif origin == "BRISTOL Bus &amp; Coach Station":
            origin = "Bristol Coach Station"
            origin_list.append(origin)
        elif origin == "LONDON VICTORIA Coach Station":
            origin = "London Victoria Coach Station"
            origin_list.append(origin)
        elif origin == "CARDIFF Coach Station, Sophia Gardens":
            origin = "Cardiff Sophia Gardens"
            origin_list.append(origin)
        else:
            origin_list.append(origin)

        destination = parsed["journeyCommand"][i]["destinationStop"]
        if destination == "University of the West of England":
            destination = "Bristol UWE"
            destination_list.append(destination)
        elif destination == "BRISTOL Bus &amp; Coach Station":
            destination = "Bristol Coach Station"
            destination_list.append(destination)
        elif destination == "LONDON VICTORIA Coach Station":
            destination = "London Victoria Coach Station"
            destination_list.append(destination)
        elif destination == "CARDIFF Coach Station, Sophia Gardens":
            destination = "Cardiff Sophia Gardens"
            destination_list.append(destination)
        else:
            destination_list.append(destination)

        departure_date = datetime.strftime(
            datetime.strptime(
                parsed["journeyCommand"][i]["departureDateTime"], "%Y-%m-%dT%H:%M:%S"
            ),
            "%A %-d %b %Y",
        )
        date_list.append(departure_date)

        departure = datetime.strftime(
            datetime.strptime(
                parsed["journeyCommand"][i]["departureDateTime"], "%Y-%m-%dT%H:%M:%S"
            ),
            "%H:%M",
        )
        departure_list.append(departure)

        arrival = datetime.strftime(
            datetime.strptime(
                parsed["journeyCommand"][i]["arrivalDateTime"], "%Y-%m-%dT%H:%M:%S"
            ),
            "%H:%M",
        )
        arrival_list.append(arrival)

        duration = ms_to_hours(parsed["journeyCommand"][i]["durationInMilliseconds"])
        duration_list.append(duration)

        price = f"£{round((parsed['journeyCommand'][i]['fare']['amountInPennies']/100*0.85), 2)}"
        price_list.append(price)

        i += 1

    # MEGABUS

    Megabus_Dictionary = {"Bristol": 13, "UWE": 14, "London": 56, "Cardiff": 20}

    Start = str(Megabus_Dictionary.get(INPUT_FROM))
    Finish = str(Megabus_Dictionary.get(INPUT_TO))
    Departure_date = str(Formatted_date)
    INPUT_NUS_CARD = "1"
    Total_Passengers = "1"
    # Return_date = '2022-07-30'

    headers = {
        "cookie": creds.MB_COOKIE,
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }
    url = (
        "https://uk.megabus.com/journey-planner/journeys?days=1&concessionCount=0&departureDate="
        + Departure_date
        + "&destinationId="
        + Finish
        + "&inboundOtherDisabilityCount=0&inboundPcaCount=0&inboundWheelchairSeated=0&nusCount="
        + str(INPUT_NUS_CARD)
        + "&originId="
        + Start
        + "&otherDisabilityCount=0&pcaCount=0&totalPassengers="
        + str(INPUT_TOTAL_PASSENGERS)
        + "&wheelchairSeated=0&sc=null"
    )
    # print(url2)

    page = requests.get(url, headers=headers, timeout=60)
    soup = str(BeautifulSoup(page.content, "html.parser"))
    your_json = (
        soup.split("window.SEARCH_RESULTS = ")[1]
        .lstrip()
        .replace("</script>\n</body>\n</html>", "")
        .rstrip()[:-1]
    )
    # your_json = re.sub('"legs".*?],', '', your_json, flags=re.DOTALL)
    parsed = json.loads(your_json)
    # print(json.dumps(parsed, indent=4, sort_keys=False))
    # print(parsed['journeys'])
    number_of_tickets = len(parsed["journeys"])
    i = 0

    while i < number_of_tickets:
        provider = "\U0001F535"
        provider_list.append(provider)

        origin = (
            parsed["journeys"][i]["origin"]["cityName"]
            + " "
            + parsed["journeys"][i]["origin"]["stopName"]
        )
        if origin == "Bristol Bond Street  (near Black's)":
            origin = "Bristol Bond Street"
            origin_list.append(origin)
        else:
            origin_list.append(origin)

        destination = (
            parsed["journeys"][i]["destination"]["cityName"]
            + " "
            + parsed["journeys"][i]["destination"]["stopName"]
        )
        if destination == "Bristol Bond Street  (near Black's)":
            destination = "Bristol Bond Street"
            destination_list.append(destination)
        else:
            destination_list.append(destination)

        departure_date = datetime.strftime(
            datetime.strptime(
                parsed["journeys"][i]["departureDateTime"], "%Y-%m-%dT%H:%M:%S"
            ),
            "%A %-d %b %Y",
        )
        date_list.append(departure_date)
        departure = datetime.strftime(
            datetime.strptime(
                parsed["journeys"][i]["departureDateTime"], "%Y-%m-%dT%H:%M:%S"
            ),
            "%H:%M",
        )
        departure_list.append(departure)
        arrival = datetime.strftime(
            datetime.strptime(
                parsed["journeys"][i]["arrivalDateTime"], "%Y-%m-%dT%H:%M:%S"
            ),
            "%H:%M",
        )
        arrival_list.append(arrival)
        try:
            duration = datetime.strftime(
                datetime.strptime(parsed["journeys"][i]["duration"], "PT%HH%MM"),
                "%-Hh %Mm",
            )
            duration_list.append(duration)
        except ValueError:
            duration = datetime.strftime(
                datetime.strptime(parsed["journeys"][i]["duration"], "PT%HH"),
                "%-Hh 00m",
            )
            duration_list.append(duration)
        price = f"£{round((parsed['journeys'][i]['price']+1), 2)}"
        price_list.append(price)

        #  Uncomment this section if you want to see the low stock count for
        #  megabus tickets
        # if parsed['journeys'][i]['lowStockCount'] is not None:
        #     print("\U0001F534", "Only", parsed['journeys']
        #           [i]['lowStockCount'], "seats left!")
        # else:
        #     pass

        i += 1

    # FLIXBUS

    Flixbus_Location_Dictionary = {
        "Cardiff": 46691,
        "London": 3848,
        "Bristol": 43131,
        "UWE": 43131,
    }

    FLIXBUS_URL = "https://flixbus.p.rapidapi.com/v1/search-trips"

    querystring = {
        "from_id": str(Flixbus_Location_Dictionary.get(INPUT_FROM)),
        "to_id": str(Flixbus_Location_Dictionary.get(INPUT_TO)),
        "currency": "GBP",
        "departure_date": str(Formatted_date),
        "number_adult": str(INPUT_TOTAL_PASSENGERS),
        "search_by": "cities",
    }

    headers = {
        "X-RapidAPI-Key": creds.FLIXBUS_API_KEY,
        "X-RapidAPI-Host": "flixbus.p.rapidapi.com",
    }

    response = requests.request(
        "GET", FLIXBUS_URL, headers=headers, params=querystring, timeout=60
    )

    soup = str(BeautifulSoup(response.text, "html.parser"))
    parsed = json.loads(soup)

    # with open("/Users/anonymous/Library/CloudStorage/OneDrive-UniversityCollegeLondon/Python_Projects/Bus Tickets/flixbusdata.html", 'r') as f:
    #     soup = str(BeautifulSoup(f, 'html.parser'))
    #     parsed = json.loads(soup)

    number_of_routes = len(parsed)
    a = 0
    while a < (number_of_routes):

        number_of_items = len(parsed[a]["items"])
        b = 0

        while b < (number_of_items):
            provider = "\U0001F7E2"
            provider_list.append(provider)

            origin = parsed[a]["from"]["name"]
            if origin == "Bristol Uni of West England":
                origin = "Bristol UWE"
                origin_list.append(origin)
            elif origin == "Bristol City Centre (Bond Street)":
                origin = "Bristol Bond Street"
                origin_list.append(origin)
            else:
                origin_list.append(origin)

            destination = parsed[a]["to"]["name"]
            if destination == "Bristol Uni of West England":
                destination = "Bristol UWE"
                destination_list.append(destination)
            elif destination == "Bristol City Centre (Bond Street)":
                destination = "Bristol Bond Street"
                destination_list.append(destination)
            else:
                destination_list.append(destination)

            Date = str(
                datetime.fromtimestamp(parsed[a]["items"][b]["departure"]["timestamp"])
            )
            departure_date = datetime.strptime(Date, "%Y-%m-%d %H:%M:%S").strftime(
                "%A %-d %b %Y"
            )
            date_list.append(departure_date)

            Departure = str(
                datetime.fromtimestamp(parsed[a]["items"][b]["departure"]["timestamp"])
            )
            departure = datetime.strptime(Departure, "%Y-%m-%d %H:%M:%S").strftime(
                "%H:%M"
            )
            departure_list.append(departure)

            Arrival = str(
                datetime.fromtimestamp(parsed[a]["items"][b]["arrival"]["timestamp"])
            )
            arrival = datetime.strptime(Arrival, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            arrival_list.append(arrival)

            duration = f"{parsed[a]['items'][b]['duration']['hour']}h {parsed[a]['items'][b]['duration']['minutes']}m"
            duration_list.append(duration)

            price = f"£{parsed[a]['items'][b]['price_total_sum']}"
            price_list.append(price)

            b += 1

        a += 1

    ###############################################################################
    # departure_list = ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    Journeys = {
        "Bus": provider_list,
        "Price": price_list,
        "Start": departure_list,
        "Finish": arrival_list,
        "Duration": duration_list,
        "Date": date_list,
        "Origin": origin_list,
        "Destination": destination_list,
    }

    pd.set_option("max_colwidth", 100)
    df = pd.DataFrame(Journeys)
    df2 = df[df["Date"] == date_list[0]]
    df3 = df2.sort_values(by=["Start"], ascending=True).reset_index(drop=True)
    df4 = df3.drop_duplicates()
    # Convert df4['start'] and df4['finish'] to datetime objects
    df4["Start"] = pd.to_datetime(df4["Start"], format="%H:%M")
    df4["Finish"] = pd.to_datetime(df4["Finish"], format="%H:%M")
    # Filter df4 to only show Start time 1 hour before the INPUT_TIME
    df4 = df4[df4["Start"] >= (pd.to_datetime(INPUT_TIME, format="%H:%M"))]
    # Filter df4 to only show Start time 9 hours after the INPUT_TIME
    df4 = df4[
        df4["Start"]
        <= (pd.to_datetime(INPUT_TIME, format="%H:%M") + timedelta(hours=1))
    ]
    # Convert df4['start'] and df4['finish'] back to strings in the format HH:MM
    df4["Start"] = df4["Start"].dt.strftime("%H:%M")
    df4["Finish"] = df4["Finish"].dt.strftime("%H:%M")

    # st.write("Key")
    st.write("\U0001F7E2 Flixbus \U0001F535 Megabus \U000026AA National Express")
    st.dataframe(df4)

    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv(index=False)

    csv = convert_df(df4)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="Bus_Price_Comparison.csv",
        # mime="text/csv",
    )
