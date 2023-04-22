import streamlit as st

st.set_page_config(
    page_title="Bus Price Comparison Tool",
    page_icon="\U0001F68C",
)


def app():
    st.title("👋 Welcome to my Bus Price Comparison Tool \n \n")
    st.write("")
    st.write("")

    st.header("🤔 Problem")
    st.write(
        """
        As a professional who recently landed a hybrid role requiring me to work in the office for 3 days a week in London,
        I faced a new challenge of finding a cost-effective and efficient way to commute from my home in Bristol.
        \n Trains in the UK are notorious for being expensive, so I turned to buses, which are far cheaper and often offer deals
        and discounts at various times of the year. However, I quickly found that searching for the best bus prices and schedules
        from multiple providers was a tedious and time-consuming task.
    """
    )
    st.write("")
    st.write("")

    st.header("💡 Solution")

    st.write(
        """
        The lack of a quick and reliable method to compare bus prices led me to develop this webapp to compare 
        National Express, Megabus and Flixbus prices all at once.
    """
    )

    st.write("")
    st.write("")

    st.header("🌟 Skills Showcased:")

    st.write(
        """
            - 🕸️ Web Scraping using official and unofficial APIs
            - 🧹 Data Cleaning with Pandas and BeautifulSoup
            - 📊 Data Analytics with Pandas
            - 📈 Data Visualization with Plotly
            - 🚀 Dashboarding and Deployment with Streamlit
            - 👥 Version Control with Git and GitHub
    """
    )


if __name__ == "__main__":
    app()
