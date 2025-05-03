"""
Name: Amanda Jacobsen
CS230: Section 4
Data: Top2000_Companies_Globally_Fixed
URL:

Description:
This program allows users to compare any of the top 2000 global companies in terms of profitability and overall
sales. The program contains features including tables, charts, and maps that allow for easy visualizations of
the status of these different companies. The website makes it easy to analyze and compare many of these companies
simultaneously. The questions the program answers include which selected company has the greatest profit, how do
the selected companies compare in sales, what is the distribution of the selected companies across countries, and
how much profit do companies different regions of the world produce.
"""

# [PY3] try and except for file reading
try:
    # imports
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    import pydeck as pdk
    import seaborn as sns

    # open file
    df = pd.read_csv("C:/Users/Amanda Jacobsen/OneDrive - Bentley University/cs230/Top2000_Companies_Globally_Fixed.csv")

except FileNotFoundError:
    st.error("CSV file not found. Please check the path.")
    st.stop()

# title the site
st.title("Top 2000 Global Companies")

# [ST1] dropdown menu for continent selection
# [DA4] filter data by one condition
# order continents alphabetically without repeats
continents = sorted(df["Continent"].unique())
selected_continent = st.sidebar.selectbox("Select a Continent", continents)     # [ST4] sidebar

# [PY1] function with default parameter
# [DA5] filter data by two conditions
# filter data function - makes sure continent and country are filtered by selections
def filter_data(df, continent, country=None):
    df = df[df["Continent"] == continent]
    if country:
        df = df[df["Country"] == country]
    return df

# use filter data function to filter by continent selection
filtered_df = filter_data(df, selected_continent)

# [ST2] dropdown menu for country selection
# order countries alphabetically without repeats
countries = sorted(filtered_df["Country"].unique())
selected_country = st.sidebar.selectbox("Select a Country", countries)

# use filter data function to filter by country & continent selection
filtered_df = filter_data(df, selected_continent, selected_country)

# [PY2] function returning two values
# get top profit company function - finds company with maximum profit out of the selected companies
def get_top_profit_company(df):
    top_row = df.loc[df["Profits ($billion)"].idxmax()]
    return top_row["Company"], top_row["Profits ($billion)"]

# lines 69,71,73,78 used AI to create
# gets list of companies in the selected country & continent and converts it to a set (so there are no duplicates)
all_companies_in_scope = set(filtered_df["Company"])
# creates list of previously selected companies from past filters
already_selected = st.session_state.get("selected_companies", [])
# combines the filtered dataframe with previously selected companies - makes sure no selections are lost when filters are changed
company_options = sorted(all_companies_in_scope.union(already_selected))

# [ST3] multiselect menu for company selection
selected_companies = st.sidebar.multiselect("Select Companies to Compare", company_options, default=already_selected)
# ensures that companies are stored even when filters are changed
st.session_state["selected_companies"] = selected_companies

# [PY4] list comprehension
# [DA1] Data cleaning/manipulation
# makes sure all selections are valid using list comprehension for selection filters
selected_companies_clean = [company for company in selected_companies if company in df["Company"].values]
# final dataframe contains the valid list of companies
final_df = df[df["Company"].isin(selected_companies_clean)]

# following steps don't occur until companies are selected
if selected_companies:
    # heading of section on top profit company
    st.write("### Top Profiting Company")

    # continues with code of the final dataframe is not empty
    if not final_df.empty:
        # [DA3] Find top value (max profit)
        # uses get top profit company function to return the highest profiting company and the profit associated with it
        top_company, top_profit = get_top_profit_company(final_df)
        st.success(f"The most profitable company selected is **{top_company}** with **${top_profit} billion** in profit.")

        # [DA2] Sorting data
        # highlight top profit function makes the row of the table of the top profiting company green
        def highlight_top_profit(row):
            return ["background-color: lightgreen"] * len(row) if row["Company"] == top_company else [""] * len(row)

        # heading for the table of selected companies
        st.write("### Selected Companies")
        # [CHART1] styled table of the dataframe
        st.dataframe(final_df.style.apply(highlight_top_profit, axis=1))

        # [CHART2] matplotlib bar chart
        # heading for sales bar chart
        st.write("### Selected Companies Ranked by Sales")
        # dataframe organized by sales in descending order
        ranked_df = final_df.sort_values(by="Sales ($billion)", ascending=False)

        # bar chart settings
        fig, ax = plt.subplots()
        # gives y-axis label and length of bars
        ax.barh(ranked_df["Company"], ranked_df["Sales ($billion)"], color="blue")
        # x-axis label
        ax.set_xlabel("Sales ($billion)")
        # title of the chart
        ax.set_title("Selected Companies Ranked by Sales")
        # y-axis organized from highest to lowest sales
        ax.invert_yaxis()
        # displays chart in streamlit
        st.pyplot(fig)

        # [SEA1] seaborn scatterplot
        # heading of the section
        st.write("### Profit vs Sales Scatterplot (Seaborn)")

        # chart settings
        fig2, ax2 = plt.subplots()
        # x-axis and y-axis assigned
        sns.scatterplot(data=final_df, x="Sales ($billion)", y="Profits ($billion)", hue="Company", ax=ax2)
        # title of scatterplot
        ax2.set_title("Profit vs Sales by Company")
        # x-axis and y-axis labels
        ax2.set_xlabel("Sales ($billion)")
        ax2.set_ylabel("Profits ($billion)")
        # displays chart in streamlit
        st.pyplot(fig2)

        # map of selected countries
        # [DA9] New columns for visualization
        # checks to make sure latitude and longitude are valid for companies in dataframe
        final_df = final_df.dropna(subset=["Latitude_final", "Longitude_final"])
        final_df = final_df[(final_df["Latitude_final"] != 0) & (final_df["Longitude_final"] != 0)]
        # calculate max profit of selected companies
        max_profit = final_df['Profits ($billion)'].max()
        # determine color of dot on map based on profit -> greater profit = brighter green
        # line 153-154 created with AI
        final_df['ProfitColor'] = final_df['Profits ($billion)'].apply(
            lambda x: [0, int(255 * x / max_profit), 0, 180])

        # heading of map section
        st.write("### Map of Selected Company Locations")

        # [MAP] pydeck map with tooltips
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            # set initial map image parameters
            initial_view_state=pdk.ViewState(
                # sets map at average latitude and longitude of selected companies
                latitude=final_df['Latitude_final'].mean(),
                longitude=final_df['Longitude_final'].mean(),
                zoom=2,
                pitch=45,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',     # map type
                    data=final_df,      # set dataframe
                    get_position='[Longitude_final, Latitude_final]',   # set location of dots on map
                    get_color='ProfitColor',    # set color of dots
                    get_radius=200000,      # set size of dots
                    pickable=True,      # allows hovering over dot to show more details

                )
            ],
            # tooltip determines the information that appears when hovering over dot
            # used AI to learn about this function
            tooltip={
                "html": "<b>{Company}</b><br>{Country}, {Continent}<br>Sales: ${Sales ($billion)}B<br>Profits: ${Profits ($billion)}B",
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                }
            }
        ))

        # [PY5] Dictionary access (keys/items)
        # counts how many times each unique country occurs in the dataframe & converts to a dictionary
        company_counts = final_df["Country"].value_counts().to_dict()
        # heading of dictionary section
        st.write("### Number of Selected Companies per Country:")
        for country, count in company_counts.items():
            # create bulleted list of each country and the number of selected companies included
            st.write(f"- {country}: {count}")

else:
    # message present until companies are selected
    st.info("Select one or more companies to compare and analyze.")
