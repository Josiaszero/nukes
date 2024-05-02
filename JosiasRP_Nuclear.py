"""
Name: Josias Rodriguez-Ponde
CS230: Section 6
Data: Nuclear Explosions 1945 - 1998
URL: jrp-nukes-data.streamlit.app

Description: This program is Streamlit-based application designed to allow users to explore nuclear
explosion data. It allows users to analyze various fields of the dataset, including visualizing explosion locations on
a map, the distribution of explosions across countries, and creating allowing the user to create
custom charts and tables based on their selected criteria.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import tempfile
import seaborn as sns


# Main DataFrame for data
df_nuke = pd.read_csv('nuclear_explosions.csv')
df_nuke.drop_duplicates(inplace=True)

# Making column names easier to type + useable with certain functions [DA1 + drop dupes above]
df_nuke = df_nuke.rename(columns={
                                    'WEAPON_SOURCE': 'country',
                                    'LOCATION': 'location',
                                    'Data.Source': 'data_source',
                                    'latitude': 'latitude',
                                    'longitude': 'longitude',
                                    'Data.Magnitude.Body': 'magnitude_body',
                                    'Data.Magnitude.Surface': 'magnitude_surface',
                                    'Location.Cordinates.Depth': 'depth',
                                    'Data.Yeild.Lower': 'yield_lower',
                                    'Data.Yeild.Upper': 'yield_upper',
                                    'Data.Purpose': 'purpose',
                                    'Data.Name': 'name',
                                    'Data.Type': 'type',
                                    'Date.Day': 'day',
                                    'Date.Month': 'month',
                                    'Date.Year': 'year'})

# Dictionary of user-friendly column names for later use
column_usf = {
                'country': 'Country',
                'location': 'Location',
                'data_source': 'Data Source',
                'latitude': 'Latitude',
                'longitude': 'Longitude',
                'magnitude_body': 'Magnitude (Body)',
                'magnitude_surface': 'Magnitude (Surface)',
                'depth': 'Depth',
                'yield_lower': 'Yield (Lower)',
                'yield_upper': 'Yield (Upper)',
                'purpose': 'Purpose',
                'name': 'Name',
                'type': 'Type',
                'day': 'Day',
                'month': 'Month',
                'year': 'Year'}


# Goes through a field/column and finds all unique values for that field and counts its frequency
def find_unique_values(data, field):  # [PY3] [DA1 / DA4, function for filtering/manipulating data]
    unique_values = {}
    unique_list = [val for val in data[field].unique()]  # [PY4]
    unique_values = data[field].value_counts().to_dict()
    return unique_list, unique_values  # [PY2]

# Runs the function for all columns
unique_data = {}

for col in df_nuke.columns:
    unique_list, unique_values = find_unique_values(df_nuke, col)
    unique_data[col] = (unique_list, unique_values)

# First Page

def main_page():
    st.title("Data Overview")

    # Grabs the name of each purpose
    unique_purpose, x = find_unique_values(df_nuke, 'purpose')

    # Assign colors to each purpose for map markers and legend
    color_map = {
                'Wr': 'green',
                'We': 'darkpurple',
                'Combat': 'darkred',
                'Pne': 'pink',
                'Se': 'blue',
                'Fms': 'black',
                'Pne:Plo': 'orange',
                'Sam': 'cadetblue',
                'Wr/Se': 'white',
                'Others': 'gray'}
    # [PY5, accessed for map markers and legend below]

    # Slider for year filter, used for map and time series chart
    min_year = int(df_nuke['year'].min())  # [DA9 - calculations on DF columns]
    max_year = int(df_nuke['year'].max())
    selected_year = st.slider("Show explosions for range:", min_year, max_year, (min_year, max_year))  # [ST1, slider]

    # Filters explosions by selected year range and only those in range show on map
    filtered_explosions = df_nuke[(df_nuke['year'] >= selected_year[0]) & (df_nuke['year'] <= selected_year[1])]  # [DA4]

    # Relevant content to display on each marker
    unique_locations = filtered_explosions[['latitude', 'longitude', 'location', 'day', 'month', 'year', 'magnitude_body', 'magnitude_surface', 'purpose']].drop_duplicates()

    # Creates folium map, taken from class example
    m = folium.Map(location=[unique_locations['latitude'].mean(), unique_locations['longitude'].mean()],
                   zoom_start=2, control_scale=True)

    # Markers for each location and content from above
    for i, row in unique_locations.iterrows(): # [DA8]
        popup_content = f"Location: {row['location']}"
        popup_content += f"<br>Date: {row['month']}/{row['day']}/{row['year']}"
        popup_content += f"<br>Magnitude Body: {row['magnitude_body']}"
        popup_content += f"<br>Magnitude Surface: {row['magnitude_surface']}"
        popup_content += f"<br>Purpose: {row['purpose'].strip()}"
        # Markers for each location, color based on color dict above with gray set as the default so "Others" don't actually need to be regrouped
        folium.Marker(location=[row['latitude'], row['longitude']],
                      popup=folium.Popup(popup_content, max_width=700),
                      icon=folium.Icon(icon='star', color=color_map.get(row['purpose'], 'gray'), prefix='fa')).add_to(m)

    # Allows user to toggle map on or off to reduce clutter
    if st.checkbox("Show Map"):
        st_folium(m, width=1000)  # [VIZ4]

        # Legend for marker colors
        with st.expander("Click to expand legend for purpose colors on map"):  # [ST2, drop down / expander]
            for purpose, color in color_map.items():
                st.write(f"<span style='color:{color}'>■</span> {purpose}", unsafe_allow_html=True)

    # Cold War influenced time series chart
    def plot_time_series(data, x, y, hue, ax):
        sns.lineplot(data=data, x=x, y=y, hue=hue, ax=ax) # ax allows you to display both USA and USSR
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Tests')
        ax.legend(title='Country')

    # Data parameter for time series
    filtered_explosions = df_nuke[((df_nuke['year'] >= selected_year[0]) & (df_nuke['year'] <= selected_year[1]))
                                  & ((df_nuke['country'] == 'USA') | (df_nuke['country'] == 'USSR'))]  # [DA5]

    # Pairs the countries/years with the amount of occurrences (.size)
    df_time_series = filtered_explosions.groupby(['year', 'country']).size().reset_index(name='count')
    chart, ax = plt.subplots(figsize=(10, 6))
    plot_time_series(df_time_series, 'year', 'count', 'country', ax)
    st.subheader('Nuclear Deployments Over Time (USA v. USSR)')  # Opted for a subheader instead of chart title
    st.pyplot(chart)  # [VIZ2]

    # Isolating countries and using the dictionary for frequency / appearances
    countries, countries_dict = find_unique_values(df_nuke, 'country')

    # Turn dictionary into dataframe for table and chart
    countries_table = pd.DataFrame(list(countries_dict.items()), columns=['Country', 'Deployment Count'])
    countries_table.set_index('Country', inplace=True) # had issue with setting index above
    countries_table.columns = ['Deployment Count']

    st.set_option('deprecation.showPyplotGlobalUse', False)  # Removes warning

    # Searches for a chart in the streamlit session
    if 'chart' not in st.session_state:
        st.session_state.chart = False

    # To open / close pie chart with a button, checkbox works the same
    def open_close():
        if st.session_state.chart:
            st.session_state.chart = False
        else:
            st.session_state.chart = True

    # To be able to call the pie chart on button click
    def display_pie_chart():
        plt.figure(figsize=(10, 10))
        sns.set_palette("pastel")
        #  Explode the overlapping entries out from other entries
        explode = [0.15 if country == 'PAKIST' else .3 if country == "INDIA" else .1 if country == "UK" else .015 for country in countries_table.index]  # [Explode idea from ChatGPT, see Docs]
        plt.pie(countries_table['Deployment Count'], labels=countries_table.index, autopct='%1.2f%%', startangle=90, explode=explode)
        plt.axis('equal')  # For scaling
        st.pyplot()  # [VIZ1]

    st.subheader('Nuclear Deployments Per Country')
    st.table(countries_table)

    # Open and close pie chart with button, I wanted text to change depending on st.session state, but couldn't figure it out
    if st.button('Open/Close Table as Pie Chart'):
        open_close()
    if st.session_state.chart:
        display_pie_chart()

    # Prepping data for heatmap
    df_heatmap = df_nuke.dropna(subset=['type'])
    heat_pivot = df_heatmap.pivot_table(index='country', columns='type', aggfunc='size', fill_value=0)

    # Displays a Heatmap of the type occurrences in data
    plt.figure(figsize=(10, 6))
    sns.heatmap(heat_pivot, cmap='RdPu', annot=True, fmt='d', linewidths=.5)
    plt.title('Nuclear Explosions by Type of Deployment')
    plt.xlabel('Type of Deployment')
    plt.ylabel('Country')
    st.pyplot()  # [VIZ3]

# Second Page
def country_data_page():
    st.title("Country Data Page")

    # Pulling the different countries from data
    unique_countries, x = find_unique_values(df_nuke, 'country')
    selected_country = st.sidebar.selectbox("Display Data for:", unique_countries)  # [ST3]

    # Displays data for selected countries
    st.subheader(f"Displaying data for: {selected_country}")
    selected_country_data = df_nuke[df_nuke['country'] == selected_country]
    sorted_data = selected_country_data.sort_values(by='yield_lower', ascending=False)  # [DA2]

    # Years had commas in it, removed with lambda function that turns x/year into a string and replaces it
    sorted_data['year'] = sorted_data['year'].apply(lambda x: str(x).replace(',', ''))  # [DA1 lambda]

    # Renamed columns using the user-friendly dictionary
    sorted_data = sorted_data.rename(columns=column_usf)

    # Set num explosions for PAKIS and INDIA which have under 5 entries, so the display doesn't say top 5 for all
    num_explosions = len(sorted_data)

    st.write(f"Showing Top {min(num_explosions, 5)} Largest Explosions by Yield for {selected_country}:")
    st.write(sorted_data.head(min(num_explosions, 5)))  # [DA3]
    st.write(f"Showing Top {min(num_explosions, 5)} Smallest Explosions by Yield for {selected_country}:")
    st.write(sorted_data.tail(min(num_explosions, 5)))

    # Pivot tables for magnitudes [DA6]
    pivot_body = selected_country_data.pivot_table(index='country', values='magnitude_body',
                                                   aggfunc=['mean', 'median', 'min', 'max', 'std'])
    pivot_surface = selected_country_data.pivot_table(index='country', values='magnitude_surface',
                                                      aggfunc=['mean', 'median', 'min', 'max', 'std'])

    # Rename columns to be User-Friendly
    pivot_body.columns = ['Mean Magnitude (Body)', 'Median Magnitude (Body)', 'Minimum Magnitude (Body)',
                          'Maximum Magnitude (Body)', 'Standard Deviation']
    pivot_surface.columns = ['Mean Magnitude (Surface)', 'Median Magnitude (Surface)', 'Minimum Magnitude (Surface)',
                             'Maximum Magnitude (Surface)', 'Standard Deviation']

    st.write("Summary of Explosion Magnitudes")
    st.write(pivot_body)
    st.write(pivot_surface)


    # Display a map with explosions for only the selected country
    m = folium.Map(location=[selected_country_data['latitude'].mean(), selected_country_data['longitude'].mean()],
                   zoom_start=3, control_scale=True)

    for i, row in selected_country_data.iterrows():
        popup_content = f"Location: {row['location']}"
        popup_content += f"<br>Date: {row['month']}/{row['day']}/{row['year']}"
        popup_content += f"<br>Magnitude Body: {row['magnitude_body']}"
        popup_content += f"<br>Magnitude Surface: {row['magnitude_surface']}"
        popup_content += f"<br>Purpose: {row['purpose']}"
        folium.Marker(location=[row['latitude'], row['longitude']],
                      popup=folium.Popup(popup_content, max_width=700),
                      icon=folium.Icon(color='darkred')).add_to(m)
    st.subheader(f'Map of All Nuclear Explosions Deployed by {selected_country}:')
    st_folium(m, width=1000)

# Third Page
def make_form_page():
    st.title("Create Your Own Table and Chart")

    unique_countries, _ = find_unique_values(df_nuke, 'country')
    selected_countries = st.multiselect("Display Data for:", unique_countries)

    if selected_countries:
        # Filter the dataframe based on selected countries
        filtered = df_nuke[df_nuke['country'].isin(selected_countries)]
        filtered.set_index('country', inplace=True)

        # Allow users to select columns for the table
        st.subheader("Select Table Columns")
        columns_without_country = [col for col in filtered.columns.tolist() if col != 'country']  # Redundant because it's the index
        selected_table_columns = st.multiselect("Select Columns:", columns_without_country)


        if selected_table_columns:
            # Displays the selected columns in a table
            table = filtered[selected_table_columns]
            table_name = st.text_input("Enter table name:")
            st.subheader(table_name)
            st.write(table)

            # Allows users to export the table as an Excel sheet, called by button click [EXTRA - Tempfile]
            def export_to_excel(table_df, table_name):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:  # Creates a temporary file not deleted when closed and already in xlsx format,
                    file_path = tmp_file.name  # Gets file path
                    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                        table_df.to_excel(writer, index=True)
                info = open(file_path, "rb")
                file_content = info.read()
                return file_content, file_path

            # Tuple with info used for download button
            file_content, file_path = export_to_excel(table, table_name)

            # Download button [Syntax from stack overflow StackOverFlow]
            st.download_button(label="Download Table as .xlsx", data=file_content, file_name=f"{table_name}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.subheader("Create Chart")
        selected_chart_columns = st.multiselect("Select Chart Columns:", filtered.columns.tolist())

        if selected_chart_columns:
            # Allow users to select columns for the chart
            st.write("""**Select Chart Options**""")
            # Check if user wants to create a frequency chart
            create_frequency_chart = st.checkbox("Create Frequency Chart")

            if create_frequency_chart:
                frequency_column = st.selectbox("Select column for Frequency Chart:", selected_chart_columns)
                chart_type = st.radio("Select Chart Type:", ["Line Chart", "Bar Chart"])

                unique_list, unique_values = unique_data[frequency_column] # [DA7, Frequency Count + Add/select columns above]

                # Make dataframe for frequency chart
                frequency_df = pd.DataFrame({"Value": unique_list, "Frequency": [unique_values[val] for val in unique_list]})

                if 'year' in frequency_column:
                    frequency_df['Value'] = frequency_df['Value'].apply(lambda x: str(x).replace(',', ''))

                # Makes the frequency chart
                st.subheader(f"Frequency Chart for {frequency_column}")
                if chart_type == "Bar Chart":
                    st.bar_chart(frequency_df, x="Value", y="Frequency", use_container_width=True) # Use container width makes chart fit with the rest of the window
                if chart_type == "Line Chart":
                    st.line_chart(frequency_df, x="Value", y="Frequency", use_container_width=True)

            else:
                with st.expander("Chart Making Guidelines"):
                    st.write("""
                    **Line Chart:**
                    - Use to visualize trends over time or for sequential data
                    - X-axis: Opt for a time-related variable such as years
                    - Y-axis: Opt for numerical data that represents values being measured over time

                    **Bar Chart:**
                    - Use to compare categorical data or show a data distribution
                    - X-axis: Opt for categorical variables such as countries, purpose, or deployment type
                    - Y-axis: Opt for numerical data that represents counts or frequencies

                    **Scatter Plot:**
                    - Use to visualize relationships between two variables
                    - X-axis: Opt for an independent variable
                    - Y-axis: Opt for a dependent variable

                    The variables you pick for your chart determine the coherence of the chart. Do have an idea of what \t
                    it is that you want to see, and if any of these chart types are suitable.""")
                    
                chart_type = st.radio("Select Chart Type:", ["Line Chart", "Bar Chart", "Scatter Plot"])
                x_axis_column = st.selectbox("Select X-axis Column:", selected_chart_columns)
                y_axis_column = st.selectbox("Select Y-axis Column:", selected_chart_columns)

                # make chart depending on what type and columns art picked
                if chart_type == "Line Chart":
                    st.line_chart(filtered, x=x_axis_column, y=y_axis_column, use_container_width=True)
                elif chart_type == "Bar Chart":
                    st.bar_chart(filtered, x=x_axis_column, y=y_axis_column, use_container_width=True)
                elif chart_type == "Scatter Plot":
                    st.scatter_chart(filtered, x=x_axis_column, y=y_axis_column, use_container_width=True)

# Introduction
def intro_page():
    with st.expander("About the Data and Site"):
        st.write("""
        **Welcome to my Nuclear Explosions Project**


        **About the Site:**
        This Streamlit application offers a user-friendly interface to gain some insight on nuclear explosions and the period. 
        In addition, although limited in functionality, there is a user interactive page where you can create tables and charts with just the data you'd like to see. 
        
        **How to Use:**
        - Navigate through the different pages using the navigation menu at the top of the page. 
        - Get a general idea of the data via the "Data Overview" page's map, visualizations and table.
        - Look closer at individual countries' explosion data on the "Individual Country Data" page. 
        - Create your own tables and charts on the "Customized Queries" page to analyze specific pieces of the data. 

        **About the Data:**
        This application uses a dataset with information on historical nuclear explosions from 1945 to 1998.
        Feel free to read about each data field below: 
        
        1. **Country**: Source of the nuclear weapon.
        2. **Location**: Geographical name of point of the explosion (ex. 'Nagasaki').
        3. **Data Source**: Source which reported the information.
        4. **Latitude**: Horizontal coordinate of the explosion.
        5. **Longitude**: Vertical coordinate of the explosion.
        6. **Magnitude (Body)**: Strength of the body wave.
        7. **Magnitude (Surface)**: Strength of the surface wave.
        8. **Depth**: Depth coordinate of explosion (Positive - above ground, Negative - below ground).
        9. **Yield (Lower)**: Lower bound estimate of explosion yield.
        10. **Yield (Upper)**: Upper bound estimate of explosion yield.
        11. **Purpose**: Reason for nuclear weapon deployment.
        12. **Name**: Name of the nuclear weapon (ex. 'Fat Man').
        13. **Type**: Method of nuclear deployment (ex. 'Airdrop').
        14. **Day**: Day of the explosion.
        15. **Month**: Month of the explosion.
        16. **Year**: Year of the explosion.

        """)

# Load selected page, main navigation
selected_page = st.radio("Page Navigation", ["Introduction", "Data Overview", "Individual Country Data", "Customized Queries"])  # [ST4, Navigation]

if selected_page == "Data Overview":
    main_page()
elif selected_page == "Individual Country Data":
    country_data_page()
elif selected_page == "Customized Queries":
    make_form_page()
elif selected_page == "Introduction":
    intro_page()
