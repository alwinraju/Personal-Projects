import streamlit as st

st.set_page_config(
    page_title="Coming Soon",
    page_icon="\U0001F6A7",
)

import streamlit as st


def app():
    st.title("🚧 Coming Soon...\n \n")
    st.write("")
    st.write("")

    st.header("\n \n 🏙️ More Cities")
    st.write(
        """
        Aiming to include a minimum of 20 additional locations that are serviced by the top 3 bus providers.
    """
    )
    st.write("")
    st.write("")

    st.header("📊 Even more data analysis")

    st.write(
        """
        I aim to collect and add data for Megabus and Flixbus tickets to extract even more insights as to which bus provider is the best value for money.
    """
    )


if __name__ == "__main__":
    app()
