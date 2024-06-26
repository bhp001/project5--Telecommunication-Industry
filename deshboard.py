import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
@st.cache_data
def load_data():
    data = pd.read_excel('Treated_df.xlsx')
    data['Start'] = pd.to_datetime(data['Start'])
    data['End'] = pd.to_datetime(data['End'])
    # Calculate total data (upload + download)
    data['Total Data (Bytes)'] = data['Total UL (Bytes)'] + data['Total DL (Bytes)']
    return data

data = load_data()

# Dashboard title
st.title('User Analytics Dashboard (Telecommunication Industry)')

# Date Range Selector
st.sidebar.header('Filter by Date Range')
start_date = st.sidebar.date_input('Start date', data['Start'].min())
end_date = st.sidebar.date_input('End date', data['Start'].max())
filtered_data = data[(data['Start'].dt.date >= start_date) & (data['Start'].dt.date <= end_date)]

# Application Selection
st.sidebar.header('Select Application Types')
applications = ['Youtube DL (Bytes)', 'Netflix DL (Bytes)', 'Gaming DL (Bytes)', 'Other DL (Bytes)']
selected_apps = st.sidebar.multiselect('Applications', applications, default=applications)
app_data = filtered_data[selected_apps].sum()

# User Identifier Selection
st.sidebar.header('Select User Identifier')
unique_ids = filtered_data['MSISDN/Number'].unique()
selected_id = st.sidebar.selectbox('User Identifier (MSISDN/Number)', unique_ids)

# Displaying filtered data usage over time
st.header('Data Usage Over Time')
if not filtered_data.empty:
    time_data = filtered_data.groupby(filtered_data['Start'].dt.date)['Total Data (Bytes)'].sum().reset_index()
    st.line_chart(time_data.rename(columns={'Start': 'index'}).set_index('index'))
else:
    st.write("No data available for the selected date range.")

# Displaying application data consumption
st.header('Application Data Consumption')
if not app_data.empty:
    st.bar_chart(app_data)
else:
    st.write("No application data available for the selected date range.")

# Displaying data for selected user
st.header(f'Data Consumption for User: {selected_id}')
user_data = filtered_data[filtered_data['MSISDN/Number'] == selected_id]
if not user_data.empty:
    st.write(f'Total Data (Bytes): {user_data["Total Data (Bytes)"].sum()}')
else:
    st.write("No data available for the selected user.")

# Correlation Heatmap
st.header('Correlation Heatmap of Numeric Features')
numeric_features = ['Total UL (Bytes)', 'Total DL (Bytes)', 'Dur. (ms)', 'Youtube DL (Bytes)', 'Netflix DL (Bytes)', 'Gaming DL (Bytes)']
if not filtered_data.empty:
    available_features = [feature for feature in numeric_features if feature in filtered_data.columns]
    if available_features:
        corr_matrix = filtered_data[available_features].corr()
        plt.figure(figsize=(10, 6))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', linewidths=.5)
        st.pyplot(plt)
    else:
        st.write("No numeric data available for the selected date range.")
else:
    st.write("No data available for the selected date range.")

# Application Data Consumption Bar Plot
st.header('Application Data Consumption')
fig, ax = plt.subplots()
app_data.plot(kind='bar', ax=ax, colormap='viridis')
ax.set_ylabel('Bytes')
ax.set_title('Data Consumption by Application')
st.pyplot(fig)

# Top 10 Users by Data Consumption
st.header('Top 10 Users by Data Consumption')
if not filtered_data.empty:
    top_users = filtered_data.groupby('MSISDN/Number')['Total Data (Bytes)'].sum().nlargest(10)
    fig, ax = plt.subplots()
    top_users.plot(kind='barh', ax=ax, color=sns.color_palette('magma', len(top_users)))
    ax.set_xlabel('Total Data (Bytes)')
    ax.set_title('Top 10 Users by Data Consumption')
    st.pyplot(fig)
else:
    st.write("No data available for the selected date range.")
