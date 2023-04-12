import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Bus Price Comparison Tool",
    page_icon="\U0001F68C",
)


def app():
    st.title("📊 Data Analysis")
    st.write(
        """
        Realizing the value of the data I had collected, I decided to conduct further analyses to answer the following questions:\n 
        For National Express tickets from <span style='font-weight:bold; font-style:italic; text-decoration:underline;'>Bristol to London</span>:\n 
        """,
        unsafe_allow_html=True,
    )

    questions = [
        "1. How far in advance should I book to get the best price?",
        "2. What is the cheapest and most expensive day to travel?",
        "3. What is the cheapest and most expensive time of day to travel?",
        "4. What is the cheapest and most expensive price I can expect to pay for a ticket?",
        "5. Does the day of the month affect the price of tickets?",
    ]
    answers = [
        "📅 Book as far in advance as possible. The price of tickets increases as the departure date/time approaches.",
        "💸 On average Thursday is the cheapest day to travel (Tuesday and Wednesday are very close too). Saturday is the most expensive.",
        "⏰ 5am is the cheapest time of day to travel.",
        "💰 £3.50 - £34.00 is the range of prices you can expect to pay for a ticket.",
        "🤯 Yes, based on the limited data I analysed, it seems that the average cost of travel is highest on the first Sunday of each month",
    ]

    # Initialize session state for answers visibility
    if "answer_visible" not in st.session_state:
        st.session_state.answer_visible = [False] * len(questions)

    # Display questions and create placeholders for answers
    answer_placeholders = []
    for idx, question in enumerate(questions):
        st.write(question)
        answer_placeholders.append(st.empty())

        # Show the answer if its visibility state is True
        if st.session_state.answer_visible[idx]:
            st.markdown(
                f"<p style='color:#2dc653;'>{answers[idx]}</p>", unsafe_allow_html=True
            )

    # Create a button to reveal/hide answers
    if st.button("Toggle Answers"):
        for idx in range(len(questions)):
            st.session_state.answer_visible[idx] = not st.session_state.answer_visible[
                idx
            ]

    st.header(":basket: Data Collection")
    st.write(
        """

        I collected the data by creating an unofficial API using the Python requests module. To ensure that the requests were not 
        blocked by the website I used a list of proxies to make the requests and rotated them alongside the user agent.
        Additionally, I implemented a 30-second delay between requests to ensure that I was not going to inadverdently DDOS the website.
        \n For each response I used the BeautifulSoup module to parse the relevant data and opted to append data after each request instead of writing 
        it to a CSV file at the end of the script in order to prevent any loss of work in the event of any errors. 
        I ran the script overnight to avoid peak times in traffic and it returned approximately 3500 rows of data in 8 hours."""
    )
    with st.expander("Show/Hide Code"):
        st.write(
            """
        ```python
import json
import random
from datetime import datetime, timedelta
import pandas as pd
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent, FakeUserAgentError
import time

BASE_URL = "https://book.nationalexpress.com/nxrest/journey/search/OUT"
PROXIES_LIST_PATH = "./Path_to_proxies/Proxy_list_verified.py"

data = {
    "coachCard": False,
    "campaignId": "DEFAULT",
    "partnerId": "NX",
    "outboundArriveByOrDepartAfter": "DEPART_AFTER",
    "inboundArriveByOrDepartAfter": "DEPART_AFTER",
    "journeyType": "RETURN",
    "operatorType": "DOMESTIC",
    "leaveDateTime": {"date": "07/04/2023", "time": "14:00"},
    "passengerNumbers": {
        "numberOfAdults": 1,
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
        "numberOnYouthCoachcard": 0,
    },
    "returnDateTime": {"date": "31/12/2023", "time": "00:00"},
    "fromToStation": {"fromStationId": "41000", "toStationId": "57366"},
    "onDemand": False,
    "languageCode": "en",
    "channelsKey": "DESKTOP",
}

ua = UserAgent()


def get_random_user_agent_header():
    try:
        user_agent = ua.random
    except FakeUserAgentError:
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
    return {"Content-Type": "application/json", "User-Agent": user_agent}


def load_proxies_list(path):
    with open(path) as f:
        return f.read().splitlines()


def get_random_proxy(proxies_list):
    return {"http": f"http://{random.choice(proxies_list)}"}


def ms_to_hours(millis):
    seconds, milliseconds = divmod(millis, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m"


def main():
    proxies_list = load_proxies_list(PROXIES_LIST_PATH)
    ticket_data = pd.DataFrame(
        columns=[
            "Departure_Stop",
            "Destination_Stop",
            "Departure_Date",
            "Arrival_Date",
            "Departure_Time",
            "Arrival_Time",
            "Duration",
            "Price",
        ]
    )
    # Instantiate a session
    session = requests.Session()
    while True:
        proxy_used = get_random_proxy(proxies_list)
        response = session.post(
            BASE_URL,
            headers=get_random_user_agent_header(),
            data=json.dumps(data),
            proxies=proxy_used,
        )
        # print the proxy used and the user agent
        print(response.status_code)
        soup = str(BeautifulSoup(response.content, "html.parser"))
        parsed = json.loads(soup)

        number_of_tickets = len(parsed["journeyCommand"])

        if number_of_tickets == 0:
            break

        last_departure_time = None

        for i in range(number_of_tickets):
            ticket = parsed["journeyCommand"][i]
            departure_time = datetime.strptime(
                ticket["departureDateTime"], "%Y-%m-%dT%H:%M:%S"
            )
            arrival_time = datetime.strptime(
                ticket["arrivalDateTime"], "%Y-%m-%dT%H:%M:%S"
            )

            ticket_info = {
                "Departure_Stop": ticket["departureStop"],
                "Destination_Stop": ticket["destinationStop"],
                "Departure_Date": departure_time.strftime("%A %dth %b %Y"),
                "Arrival_Date": arrival_time.strftime("%A %dth %b %Y"),
                "Departure_Time": departure_time.strftime("%-I:%M%p"),
                "Arrival_Time": arrival_time.strftime("%-I:%M%p"),
                "Duration": ms_to_hours(ticket["durationInMilliseconds"]),
                "Price": f"£{round((ticket['fare']['amountInPennies'] / 100), 2)}",
            }

            # ticket_data = ticket_data.append(ticket_info, ignore_index=True)
            ticket_data = pd.concat(
                [ticket_data, pd.DataFrame([ticket_info])], ignore_index=True
            )

            # Make ticket_info a dataframe and append to the csv
            pd.DataFrame([ticket_info]).to_csv(
                "./Mined_Data.csv",
                mode="a",
                header=False,
                index=False,
            )

            last_departure_time = departure_time

        if last_departure_time is not None:
            last_departure_time += timedelta(minutes=1)
            data["leaveDateTime"]["date"] = last_departure_time.strftime("%d/%m/%Y")
            data["leaveDateTime"]["time"] = last_departure_time.strftime("%H:%M")
        print(ticket_data)
        time.sleep(30)


if __name__ == "__main__":
    main()

        """
        )
    st.header(":broom: Data Cleaning")

    st.write(
        """
        The resulting csv file was cleaned using Pandas and new features were 
        created from the date and time columns to allow for easier analysis.

    """
    )

    with st.expander("Show/Hide Code"):
        st.write(
            """
        ```python
import pandas as pd

pd.set_option('display.max_colwidth', 100)
raw_data = pd.read_csv('./National Express by Month.csv',
                        names=['Departure Stop', 'Destination Stop', 'Departure Date', 'Arrival Date', 'Departure Time', 'Arrival Time', 'Duration', 'Price'])

df = raw_data.copy()

# Replace & with 'and' and convert to sentence case
df['Departure Stop'] = df['Departure Stop'].str.replace('&', 'and').str.title()
df['Destination Stop'] = df['Destination Stop'].str.replace('&', 'and').str.title()

# Remove the £ symbol and convert to float
df['Price'] = df['Price'].str.replace('£', '').astype(float)

# Create new columns for Departure Date Time and Arrival Date Time
df['Departure Date Time'] = pd.to_datetime(df['Departure Date'] + ' ' + df['Departure Time'])
df['Arrival Date Time'] = pd.to_datetime(df['Arrival Date'] + ' ' + df['Arrival Time'])

# Convert the Duration column to timedelta
df['Duration'] = pd.to_timedelta(df['Duration'])

# Filter Departure_Stop to only include Bristol
df = df[df['Departure Stop'] == 'Bristol Bus And Coach Station']

# Select required columns
df = df[['Departure Stop', 'Destination Stop', 'Departure Date Time', 'Arrival Date Time', 'Duration', 'Price']]

# Create new columns for departure hour, day of the week, month, day in the month, departure date, and arrival date
df['Departure Hour'] = df['Departure Date Time'].dt.hour
df['Departure Day of the Week'] = df['Departure Date Time'].dt.day_name()
df['Departure Month'] = df['Departure Date Time'].dt.month_name()
df['Day in the Month'] = df['Departure Date Time'].dt.day
df['Departure Date'] = df['Departure Date Time'].dt.date
df['Arrival Date'] = df['Arrival Date Time'].dt.date

# Drop rows where we do not have a full day's worth of ticket data
df = df[(df['Arrival Date'] != df['Arrival Date'].max()) & (df['Arrival Date'] != df['Arrival Date'].min())]

# Reset the index
df = df.reset_index(drop=True)
nx_coach = df.copy()
nx_coach.tail()
        """
        )

    st.header(":chart_with_downwards_trend: Data Visualization")

    st.write(
        """
        I decided to visualize the data using Plotly as it offers interactive graphs and charts that allow users to explore 
        the data in-depth. Secondly, the library also provides a wide range of customizable options for 
        colors, fonts, and layout that can be tailored to match the overall aesthetic of the webapp. 
        Overall, I feel that Plotly is a good choice for creating visually appealing, and engaging data 
        visualizations that enhance the users understanding of the data.
    """
    )

    with st.expander("Show/Hide Code"):
        st.write(
            """
        ```python
    nx_coach = pd.read_csv(
        "./National Express Data Cleaned.csv"
    )
    nx_coach["Departure Date Time"] = pd.to_datetime(nx_coach["Departure Date Time"])
    nx_coach.groupby(pd.Grouper(key='Departure Date Time', freq='M'))['Price'].mean()

    # Create a plotly line chart
    fig = px.line(nx_coach.groupby(pd.Grouper(key='Departure Date Time', freq='M'))['Price'].mean(), x=nx_coach.groupby(pd.Grouper(key='Departure Date Time', freq='M'))['Price'].mean().index, y='Price')

    # Customize the chart
    fig.update_layout(title='National Express Coach Prices by Month',
                    xaxis_title='Week',
                    yaxis_title='Price (£)')

    # Set xticks as the index of the dataframe
    fig.update_xaxes(ticktext=nx_coach.groupby(pd.Grouper(key='Departure Date Time', freq='M'))['Price'].mean().index.strftime('%b-%y'),
                        tickvals=nx_coach.groupby(pd.Grouper(key='Departure Date Time', freq='M'))['Price'].mean().index)

    fig.show()
        """
        )
    nx_coach = pd.read_csv("./National Express Data Cleaned.csv")
    nx_coach["Departure Date Time"] = pd.to_datetime(nx_coach["Departure Date Time"])
    nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="M"))["Price"].mean()

    # Create a plotly line chart
    fig = px.line(
        nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="M"))[
            "Price"
        ].mean(),
        x=nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="M"))["Price"]
        .mean()
        .index,
        y="Price",
    )

    # Customize the chart
    fig.update_layout(
        title="National Express Coach Prices by Month",
        xaxis_title="Week",
        yaxis_title="Price (£)",
    )

    # Set xticks as the index of the dataframe
    fig.update_xaxes(
        ticktext=nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="M"))[
            "Price"
        ]
        .mean()
        .index.strftime("%b-%y"),
        tickvals=nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="M"))[
            "Price"
        ]
        .mean()
        .index,
    )

    st.plotly_chart(fig)
    st.write(
        """:worm: No surprises here! The earlier you book your ticket, the better the price.
        As the saying goes 'the early bird catches the worm' and this is 
        certainly true when it comes to booking coach tickets. """
    )

    with st.expander("Show/Hide Code"):
        st.write(
            """
        ```python
    nx_coach = pd.read_csv(
        "/Users/anonymous/Library/CloudStorage/OneDrive-UniversityCollegeLondon/Python_Projects/Bus_Price_Comparison_App/Bus_Price_App/pages/National Express Data Cleaned.csv"
    )
    nx_coach["Departure Date Time"] = pd.to_datetime(nx_coach["Departure Date Time"])
    nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="W"))["Price"].mean()
    # Create a plotly line chart
    fig2 = px.line(
        nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="W"))[
            "Price"
        ].mean(),
        x=nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="W"))["Price"]
        .mean()
        .index,
        y="Price",
    )

    # Customize the chart
    fig2.update_layout(
        title="National Express Coach Prices by Week",
        xaxis_title="Week",
        yaxis_title="Price (£)",
    )
    fig2.show()
        """
        )

    nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="W"))["Price"].mean()
    # Create a plotly line chart
    fig2 = px.line(
        nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="W"))[
            "Price"
        ].mean(),
        x=nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="W"))["Price"]
        .mean()
        .index,
        y="Price",
    )

    # Customize the chart
    fig2.update_layout(
        title="National Express Coach Prices by Week",
        xaxis_title="Week",
        yaxis_title="Price (£)",
    )
    st.plotly_chart(fig2)

    st.write(
        """:thinking_face: This is quite peculiar! The price of coach tickets seems to be higher on the first weekend of every month! I cant seem to 
     find any reason for this. If you have any ideas, please let me know! I welcome all feedback and suggestions on how to improve this webapp. """
    )

    with st.expander("Show/Hide Code"):
        st.write(
            """
        ```python
    nx_coach = pd.read_csv(
        "/Users/anonymous/Library/CloudStorage/OneDrive-UniversityCollegeLondon/Python_Projects/Bus_Price_Comparison_App/Bus_Price_App/pages/National Express Data Cleaned.csv"
    )
    nx_coach["Departure Date Time"] = pd.to_datetime(nx_coach["Departure Date Time"])
    nx_coach_day = nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="D"))[
        "Price"
    ].mean()

    # Create a plotly line chart
    fig3 = px.line(nx_coach_day, x=nx_coach_day.index, y="Price")

    # Customize the chart
    fig3.update_layout(
        title="National Express Coach Prices by Day",
        xaxis_title="Date",
        yaxis_title="Price (£)",
    )

    # Display the Plotly chart
    fig3.show()
        """
        )

    nx_coach_day = nx_coach.groupby(pd.Grouper(key="Departure Date Time", freq="D"))[
        "Price"
    ].mean()

    # Create a plotly line chart
    fig3 = px.line(nx_coach_day, x=nx_coach_day.index, y="Price")

    # Customize the chart
    fig3.update_layout(
        title="National Express Coach Prices by Day",
        xaxis_title="Date",
        yaxis_title="Price (£)",
    )

    # Display the Plotly chart
    st.plotly_chart(fig3)

    with st.expander("Show/Hide Code"):
        st.write(
            """
        ```python
        nx_coach = pd.read_csv(
            "/Users/anonymous/Library/CloudStorage/OneDrive-UniversityCollegeLondon/Python_Projects/Bus_Price_Comparison_App/Bus_Price_App/pages/National Express Data Cleaned.csv"
        )
        nx_coach["Departure Date Time"] = pd.to_datetime(nx_coach["Departure Date Time"])
        # Calculate the mean and standard deviation of prices by weekday
        nx_coach_weekday = nx_coach.groupby(nx_coach['Departure Date Time'].dt.weekday)['Price'].agg(['mean'])

        # Create a plotly bar chart with error bars
        fig4 = px.bar(nx_coach_weekday, x=nx_coach_weekday.index, y='mean')

        # Customize the chart
        fig4.update_layout(title='National Express Average Price by Departure Day',
                        xaxis_title='Departure Day (Bristol-London)',
                        yaxis_title='Average Price (£)')

        # Set the x-axis tick labels to show abbreviated weekday names
        fig4.update_xaxes(ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                        tickvals=[0, 1, 2, 3, 4, 5, 6])

        # Set the y ticks to be to 2 decimal places
        fig4.update_yaxes(tickformat=".2f")
        # Start y axis from 4
        fig4.update_yaxes(range=[4, 6])

        # Show the chart
        fig4.show()
        """
        )
    # Calculate the mean and standard deviation of prices by weekday
    nx_coach_weekday = nx_coach.groupby(nx_coach["Departure Date Time"].dt.weekday)[
        "Price"
    ].agg(["mean"])

    # Create a plotly bar chart with error bars
    fig4 = px.bar(nx_coach_weekday, x=nx_coach_weekday.index, y="mean")

    # Customize the chart
    fig4.update_layout(
        title="National Express Average Price by Departure Day",
        xaxis_title="Departure Day",
        yaxis_title="Average Price (£)",
    )

    # Set the x-axis tick labels to show abbreviated weekday names
    fig4.update_xaxes(
        ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        tickvals=[0, 1, 2, 3, 4, 5, 6],
    )

    # Set the y ticks to be to 2 decimal places
    fig4.update_yaxes(tickformat=".2f")
    # Start y axis from 4
    fig4.update_yaxes(range=[4, 6])

    # Show the chart
    st.plotly_chart(fig4)

    st.write(
        """:bulb: From looking at these graphs there appears to be weekly seasonality in the data,
            showing that the price of tickets is lower between Tuesday-Thursday and higher during the weekend. This is likely due to the fact that
            the majority of people travel from Bristol into London for the weekend rather than on a weekday, and therefore the demand for 
            tickets is higher causing the price to increase. """
    )

    with st.expander("Show/Hide Code"):
        st.write(
            """
        ```python
        nx_coach = pd.read_csv(
            "/Users/anonymous/Library/CloudStorage/OneDrive-UniversityCollegeLondon/Python_Projects/Bus_Price_Comparison_App/Bus_Price_App/pages/National Express Data Cleaned.csv"
        )
        nx_coach["Departure Date Time"] = pd.to_datetime(nx_coach["Departure Date Time"])
        nx_coach.groupby(nx_coach['Departure Date Time'].dt.hour)['Price'].mean()

        # Create a plotly bar chart to show average ticket price by departure hour
        fig5 = px.bar(nx_coach.groupby(nx_coach['Departure Date Time'].dt.hour)['Price'].mean(),
                    x=nx_coach.groupby(nx_coach['Departure Date Time'].dt.hour)['Price'].mean().index, y='Price')

        # Customize the chart
        fig5.update_layout(title='Average Ticket Price by Departure Hour',
                            xaxis_title='Departure Hour (Bristol-London)',
                            yaxis_title='Average Price (£)')
        # Set the y ticks to be to 2 decimal places
        fig5.update_yaxes(tickformat=".2f")
        # Start y axis from 3.50
        fig5.update_yaxes(range=[0.00, 26])

        # Show the chart
        fig5.show()
        """
        )

    # Create a plotly bar chart to show average ticket price by departure hour
    fig5 = px.bar(
        nx_coach.groupby(nx_coach["Departure Date Time"].dt.hour)["Price"].mean(),
        x=nx_coach.groupby(nx_coach["Departure Date Time"].dt.hour)["Price"]
        .mean()
        .index,
        y="Price",
    )

    # Customize the chart
    fig5.update_layout(
        title="Average Price by Departure Hour",
        xaxis_title="Departure Hour",
        yaxis_title="Average Price (£)",
    )
    # Set the y ticks to be to 2 decimal places
    fig5.update_yaxes(tickformat=".2f")
    # Start y axis from 3.50
    fig5.update_yaxes(range=[0.00, 26])

    # Show the chart
    st.plotly_chart(fig5)

    st.write(
        """:clock5: It appears that 5am is the cheapest time to travel from Bristol to London, with night-time fares from 12am to 4am being
     3-5x more expensive! Could this be because you are on an empty bus and National Express is trying to make up for the loss of revenue?
     Or could it also be that demand is so low that National Express are increasing prices to dissuade people from travelling at night so they
     can cut these scheduled buses altogether? It looks like they have already done this for the 1am bus, as there are no buses scheduled for
     departure in this hour."""
    )

    st.subheader(":coffee: Liked this analysis?")
    st.write(
        """If you found this analysis helpful and would like to support me in continuing this project or others like this, 
        please consider <a href='https://www.buymeacoffee.com/alwinrajuG' target='_blank'>buying me a coffee!</a>
        As an independent analyst, every contribution helps me to invest 
        more time and resources into conducting deeper and more comprehensive analyses. With your support, 
        I can provide even more valuable insights into various topics and continue to improve this webapp. 
        Thank you for coming this far and reading!""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    app()
