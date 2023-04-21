import streamlit as st

st.set_page_config(
    page_title="Coming Soon",
    page_icon="\U0001F6A7",
)


def app():
    with st.container():
        st.markdown("# ✅ Completed")
        st.markdown(
            """
            ### 🎓 Student Tickets
            - Added functionality to compare student tickets on the comparison tool.
            ### 🏙️ More Cities
            - Now includes a total of 27 locations that are serviced by the top 3 bus providers."""
        )

    st.write("")
    st.write("")

    with st.container():
        st.title("🚧 Coming Soon...")
        st.markdown(
            """
            ### 📊 More Data Analysis
            - Aiming to add analyses of Megabus and Flixbus tickets to extract even more insights as to which bus provider is the best value for money.
            ### 👶 Childrens Tickets
            - Aiming to add functionality to include childrens tickets to the comparison tool.
        """
        )


if __name__ == "__main__":
    app()
