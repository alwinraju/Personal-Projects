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

    st.header("📊 Data Analysis")

    st.write(
        """
        By exploring the data, I aim to identify the optimal times to book and how far in advance to book tickets.
    """
    )


if __name__ == "__main__":
    app()
