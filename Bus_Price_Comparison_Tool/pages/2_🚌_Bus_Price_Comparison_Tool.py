""" Script compares bus prices from different providers and outputs the results in a table."""

import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from fake_useragent import UserAgent, FakeUserAgentError
import streamlit as st
import locations

st.set_page_config(
    page_title="Bus Price Comparison Tool",
    page_icon="\U0001F68C",
)

st.title("🚌 Compare UK Intercity Bus Prices")
cities = [
    "Birmingham",
    "Bradford",
    "Bridgwater",
    "Bristol",
    "Cambridge",
    "Cardiff",
    "Chester",
    "Exeter",
    "Lancaster",
    "Leeds",
    "Leicester",
    "Liverpool",
    "London",
    "Luton",
    "Manchester",
    "Middlesbrough",
    "Northampton",
    "Nottingham",
    "Preston",
    "Reading",
    "Sheffield",
    "Stoke-on-Trent",
    "Sunderland",
    "Swansea",
    "Taunton",
    "Warrington",
    "Yeovil",
]
# Create dropdown fields for departure and destination
col1, col2 = st.columns(2)

# Check if session state exists and initialize if not
if "dropdown1_index" not in st.session_state:
    st.session_state.dropdown1_index = 3
if "dropdown2_index" not in st.session_state:
    st.session_state.dropdown2_index = 12

with col1:
    INPUT_FROM = st.selectbox("From", cities, index=st.session_state.dropdown1_index)

with col2:
    INPUT_TO = st.selectbox("To", cities, index=st.session_state.dropdown2_index)

    # Update session state with the selected indices
    st.session_state.dropdown1_index = cities.index(INPUT_FROM)
    st.session_state.dropdown2_index = cities.index(INPUT_TO)

button_col1, button_col2 = st.columns(2)
with button_col1:
    # Create a button for swapping the selections
    if st.button("Swap Locations"):
        # Swap the session state selections
        st.session_state.dropdown1_index, st.session_state.dropdown2_index = (
            st.session_state.dropdown2_index,
            st.session_state.dropdown1_index,
        )

        # Update the select boxes with the new selections
        st.experimental_rerun()

# Create input field for departure date
with col1:
    streamlit_date = st.date_input(
        "Departure Date", datetime.now(), min_value=datetime.now()
    )
# Convert date to string in format dd/mm/yyyy
INPUT_DATE = datetime.strptime(str(streamlit_date), "%Y-%m-%d").strftime("%d/%m/%Y")

# Create an input field for depart after time, make it default to now and force it to be in the format hh:mm
# col1, col2 = st.columns(2)
with col2:
    INPUT_TIME = st.time_input("Depart After", datetime.now()).strftime("%H:%M")

# Create input fields for number of passengers
with col1:
    INPUT_TOTAL_PASSENGERS = st.number_input(
        "Number of Adults", min_value=1, max_value=10, step=1, value=1
    )
    INPUT_NUS_CARD = st.number_input(
        "NUS/Totum Card Passengers", min_value=0, max_value=10, step=1, value=1
    )
with col2:
    INPUT_COACH_CARD = st.number_input(
        "National Express Coach Card Passengers",
        min_value=0,
        max_value=10,
        step=1,
        value=1,
    )


def get_random_user_agent():
    try:
        user_agent = UserAgent.random
    except FakeUserAgentError:
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
    return user_agent


# Create button to initiate price comparison
if st.button("Compare Prices", type="primary"):
    with st.spinner("Searching Tickets..."):
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

        NATIONAL_EXPRESS_URL = (
            "https://book.nationalexpress.com/nxrest/journey/search/OUT"
        )

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
                "fromStationId": (locations.NX_From.get(INPUT_FROM)),
                "toStationId": (locations.NX_To.get(INPUT_TO)),
            },
            "onDemand": False,
            "languageCode": "en",
            "channelsKey": "DESKTOP",
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://book.nationalexpress.com",
            "Content-Type": "application/json",
            "Cookie": st.secrets["NX_COOKIE"],
            "Content-Length": "795",
            "Accept-Language": "en-GB,en;q=0.9",
            "Host": "book.nationalexpress.com",
            # Select a random user agent from user agent list
            "User-Agent": str(get_random_user_agent()),
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
                    parsed["journeyCommand"][i]["departureDateTime"],
                    "%Y-%m-%dT%H:%M:%S",
                ),
                "%A %-d %b %Y",
            )
            date_list.append(departure_date)

            departure = datetime.strftime(
                datetime.strptime(
                    parsed["journeyCommand"][i]["departureDateTime"],
                    "%Y-%m-%dT%H:%M:%S",
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

            duration = ms_to_hours(
                parsed["journeyCommand"][i]["durationInMilliseconds"]
            )
            duration_list.append(duration)

            price = f"£{round((parsed['journeyCommand'][i]['fare']['amountInPennies']/100*0.85), 2)}"
            price_list.append(price)

            i += 1

        # MEGABUS

        Start = locations.Megabus.get(INPUT_FROM)
        Finish = locations.Megabus.get(INPUT_TO)
        Departure_date = str(Formatted_date)
        INPUT_NUS_CARD = "1"
        Total_Passengers = "1"

        headers = {
            "cookie": st.secrets["MB_COOKIE"],
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
        clean_json = (
            soup.split("window.SEARCH_RESULTS = ")[1]
            .lstrip()
            .replace("</script>\n</body>\n</html>", "")
            .rstrip()[:-1]
        )
        parsed = json.loads(clean_json)
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

        FLIXBUS_URL = "https://flixbus.p.rapidapi.com/v1/search-trips"

        querystring = {
            "from_id": str(locations.Flixbus.get(INPUT_FROM)),
            "to_id": str(locations.Flixbus.get(INPUT_TO)),
            "currency": "GBP",
            "departure_date": str(Formatted_date),
            "number_adult": str(INPUT_TOTAL_PASSENGERS),
            "search_by": "cities",
        }

        headers = {
            "X-RapidAPI-Key": st.secrets["FLIXBUS_API_KEY"],
            "X-RapidAPI-Host": "flixbus.p.rapidapi.com",
        }

        response = requests.request(
            "GET", FLIXBUS_URL, headers=headers, params=querystring, timeout=60
        )

        soup = str(BeautifulSoup(response.text, "html.parser"))
        parsed = json.loads(soup)

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
                    datetime.fromtimestamp(
                        parsed[a]["items"][b]["departure"]["timestamp"]
                    )
                )
                departure_date = datetime.strptime(Date, "%Y-%m-%d %H:%M:%S").strftime(
                    "%A %-d %b %Y"
                )
                date_list.append(departure_date)

                Departure = str(
                    datetime.fromtimestamp(
                        parsed[a]["items"][b]["departure"]["timestamp"]
                    )
                )
                departure = datetime.strptime(Departure, "%Y-%m-%d %H:%M:%S").strftime(
                    "%H:%M"
                )
                departure_list.append(departure)

                Arrival = str(
                    datetime.fromtimestamp(
                        parsed[a]["items"][b]["arrival"]["timestamp"]
                    )
                )
                arrival = datetime.strptime(Arrival, "%Y-%m-%d %H:%M:%S").strftime(
                    "%H:%M"
                )
                arrival_list.append(arrival)

                duration = f"{parsed[a]['items'][b]['duration']['hour']}h {parsed[a]['items'][b]['duration']['minutes']}m"
                duration_list.append(duration)

                price = f"£{parsed[a]['items'][b]['price_total_sum']}"
                price_list.append(price)

                b += 1

            a += 1

        ###############################################################################
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
