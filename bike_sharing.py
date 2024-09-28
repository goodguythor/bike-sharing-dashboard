import streamlit as st
import pandas as pd
import altair as alt

DAY_PATH = 'dataset/day.csv'
HOUR_PATH = 'dataset/hour.csv'

st.set_page_config(
    page_title='Bike Sharing Dashboard',
    layout='wide'
)

@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

# Load data
daily_data = load_data(DAY_PATH)
hourly_data = load_data(HOUR_PATH)

# Sidebar buttons to switch between views
st.sidebar.title("Bike Sharing Dashboard")

# Fix season columns format
daily_data['season'] = daily_data['season'].replace({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'})
hourly_data['season'] = hourly_data['season'].replace({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'})

# Fix weather columns format
daily_data['weathersit'] = daily_data['weathersit'].replace({1: 'Clear/Cloudy', 2: 'Mist', 3: 'Light Rain/Snow', 4: 'Heavy Rain/Snow'})
hourly_data['weathersit'] = hourly_data['weathersit'].replace({1: 'Clear/Cloudy', 2: 'Mist', 3: 'Light Rain/Snow', 4: 'Heavy Rain/Snow'})

# Fix working day columns format
hourly_data['workingday'] = hourly_data['workingday'].replace({0: 'Non Working Day', 1: 'Working Day'})

# Adjust the hour format
hourly_data['hr']+=1

year_option = st.sidebar.selectbox(
    'Select Year',
    (2011, 2012)
)

hour_option = st.sidebar.selectbox(
    'Select Hour',
    tuple(range(1,25))
)

season_option = st.sidebar.selectbox(
    'Select Season',
    ('Winter', 'Spring', 'Summer', 'Fall')
)

# Create columns to divide dashboard into 3
col1, col2, col3 = st.columns((1.5, 3, 2), gap='medium')

# First column
with col1:
    # About
    st.subheader('About')
    st.markdown("""
        - Data: [Bike Sharing Dataset](https://drive.google.com/file/d/1RaBmV6Q6FYWU4HWZs80Suqd7KQC34diQ/view?usp=sharing)   

        - Weather Based: The average amount of bikes shared per hour for each weather

        - Hour Based: The average amount of bikes shared for each hour
                
        - Weather Occurences: Total occurrences of each weather during each hour for each season
        
        - Working Day: The average amount of bike shared during each hour for each season between working day and non working day        
                
        - Peak & Low: Count the maximum & minimum bike shared per day & hour for this year
    """)

    # Draw the first table
    st.subheader('Best Season')
    season_temp_count_data = daily_data[daily_data['yr']==(year_option-2011)].groupby('season')[['cnt', 'temp']].mean().sort_values(by='cnt', ascending=False)
    season_temp_count_data['temp'] *= (47) - 8
    season_temp_count_data.columns = ['Average Daily Bike Shared Count', 'Average Daily Temperature']
    season_temp_count_data.rename_axis('Season', inplace=True)
    st.table(data=season_temp_count_data)

# Second column
with col2:
    st.subheader('Weather Based')

    # Pick the data
    weather_data = hourly_data[(hourly_data['yr'] == (year_option - 2011)) & (hourly_data['season'] == season_option)].groupby('weathersit')['cnt'].mean().reset_index()
    
    # Plotting the weather data
    chart = alt.Chart(weather_data).mark_bar(color='blue').encode(
        x=alt.X('weathersit:O', title='Weather Situation'),  # Categorical axis for weather situation
        y=alt.Y('cnt:Q', title='Average Hourly Bike Shared Counts'),  # Quantitative axis for average bike counts
        tooltip=['weathersit', 'cnt']  # Tooltip showing details on hover
    ).properties(
        title='Hourly Bike Shared Counts'
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader('Hour Based')

    # Pick the data
    hourly_bike_count = hourly_data[(hourly_data['yr'] == (year_option - 2011)) & (hourly_data['season'] == season_option)].groupby('hr')['cnt'].mean().reset_index()
    
    # Plotting the weather data
    chart = alt.Chart(hourly_bike_count).mark_bar(color='blue').encode(
        x=alt.X('hr:O', title='Hour'),  # Categorical axis for weather situation
        y=alt.Y('cnt:Q', title='Average Hourly Bike Shared Counts'),  # Quantitative axis for average bike counts
        tooltip=['hr', 'cnt']  # Tooltip showing details on hover
    ).properties(
        title='Hourly Bike Shared Counts'
    )
    st.altair_chart(chart, use_container_width=True)

# Third column
with col3:
    st.subheader('Total Bike Shared')

    # Calculate the total bike shared during that year
    total_bikes_shared = daily_data[daily_data['yr'] == (year_option - 2011)]['cnt'].sum()
    total_bikes_shared_season = daily_data[(daily_data['yr'] == (year_option - 2011)) & (daily_data['season'] == season_option)]['cnt'].sum()

    # Draw the total year & season
    total_year, total_season = st.columns(2)
    total_year.metric(label='Total Year', value=f"{total_bikes_shared / 1_000_000:.1f}M")
    total_season.metric(label='Total Season', value=f"{total_bikes_shared_season / 1_000:.1f}K")

    st.subheader('Peak & Low')
    max_day = daily_data[daily_data['yr'] == (year_option - 2011)]['cnt'].max()
    min_day = daily_data[daily_data['yr'] == (year_option - 2011)]['cnt'].min()
    max_hour = hourly_data[hourly_data['yr'] == (year_option - 2011)]['cnt'].max()
    min_hour = hourly_data[hourly_data['yr'] == (year_option - 2011)]['cnt'].min()

    mxday, mnday, mxhour, mnhour = st.columns(4)
    mxday.metric(label='Peak Day', value=max_day)
    mnday.metric(label='Lowest Day', value=min_day)
    mxhour.metric(label='Peak Hour', value=max_hour)
    mnhour.metric(label='Lowest Hour', value=min_hour)

    # Weather occurrence during those year & season
    st.subheader('Weather Occurrences')
    # Draw the total year & season
    clear, mist, light, heavy = st.columns(4)
    # Extract counts for each weather condition
    counts = {
        'Clear/Cloudy': 0,
        'Mist': 0,
        'Light Rain/Snow': 0,
        'Heavy Rain/Snow': 0
    }

    # Calculate total occurences of each weather
    total_weather = hourly_data[(hourly_data['yr'] == (year_option - 2011)) & (hourly_data['season'] == season_option) & (hourly_data['hr'] == hour_option)].groupby('weathersit').size().reset_index(name='count')

    # Fill the counts dictionary based on occurrences
    for index, row in total_weather.iterrows():
        if row['weathersit'] in counts:
            counts[row['weathersit']] = row['count']
    
    # Display the metrics in the respective columns
    clear.metric(label='Clear/Cloudy', value=counts['Clear/Cloudy'])
    mist.metric(label='Mist', value=counts['Mist'])
    light.metric(label='Light Rain/Snow', value=counts['Light Rain/Snow'])
    heavy.metric(label='Heavy Rain/Snow', value=counts['Heavy Rain/Snow'])

    st.subheader('Working Day')
    working_day = hourly_data[(hourly_data['yr'] == (year_option - 2011)) & (hourly_data['season'] == season_option) & (hourly_data['hr'] == hour_option)].groupby('workingday')['cnt'].mean().reset_index()
    # Create a pie/donut chart using Altair
    chart = alt.Chart(working_day).mark_arc(innerRadius=50).encode(
        color=alt.Color(field='workingday', type='nominal', title='Working Day'),
        theta=alt.Theta(field='cnt', type='quantitative', title='Average Bikes Shared'),
        tooltip=['cnt', 'workingday']
    ).properties(
        title='Working Day Comparison'
    )

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)