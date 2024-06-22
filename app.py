import streamlit as st
import pandas as pd
import folium
from streamlit.components.v1 import html
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv('/content/ASEAN-Air-Pollution---Capstone-G5-DS-GreatEdu/dataset/ASEAN Clean Cluster.csv')

# Colors and warnings based on cluster
cluster_colors = {0: 'blue', 1: 'orange', 2: 'red'}
cluster_descriptions = {0: 'Kualitas udara sehat', 1: 'Kualitas udara buruk', 2: 'Kualitas udara sangat buruk'}
cluster_warnings = {
    1: "Kualitas udara buruk. Demi kesehatan Anda, mohon berhati-hati saat berada di luar rumah dan gunakan masker jika perlu.😷",
    2: "Kualitas udara sangat buruk. Tidak sehat bagi kelompok sensitif. ☠️"
}

# Sidebar
st.sidebar.title("Filter")
selected_country = st.sidebar.selectbox("Pilih Negara", df['Country'].unique())
view_option = st.sidebar.radio("Tampilkan", ("Informasi Kota", "10 Kota dengan AQI Tertinggi"))

# Header
col1, col2 = st.columns([1, 3])
with col1:
    st.image("/content/ASEAN-Air-Pollution---Capstone-G5-DS-GreatEdu/asset/asean_logo.png", width=150)
with col2:
    st.title("Informasi Polusi Kota di Negara ASEAN")

# Filter dataframe based on selected country
filtered_df = df[df['Country'] == selected_country]

# Function to convert DataFrame to HTML with cluster color highlight
def render_dataframe(df, cluster_col, color):
    html = df.to_html(index=False, escape=False)
    html = html.replace(
        f'<td>{cluster_col}</td>', f'<td style="color:{color};">{cluster_col}</td>'
    )
    return html

# Display 10 cities with highest AQI
if view_option == "10 Kota dengan AQI Tertinggi":
    top_cities = filtered_df.nlargest(10, 'AQI Value')
    st.header(f"10 Kota dengan AQI Tertinggi di {selected_country}")
    
    st.table(top_cities[['Country', 'City', 'cluster', 'AQI Value', 'CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value']])
    
    # Create map
    m = folium.Map(location=[top_cities['Latitude'].mean(), top_cities['Longitude'].mean()], zoom_start=8)
    
    # Add markers to map for each city
    for idx, row in top_cities.iterrows():
        if 90 >= row['Latitude'] >= -11 and 141 >= row['Longitude'] >= 95:
            if row['cluster'] == 0:
                icon = folium.Icon(icon='0', prefix='fa', color='blue')
            elif row['cluster'] == 1:
                icon = folium.Icon(icon='1', prefix='fa', color='orange')
            elif row['cluster'] == 2:
                icon = folium.Icon(icon='2', prefix='fa', color='red')
            else:
                icon = folium.Icon(icon='question', prefix='fa', color='gray')

            popup_text = (
                f"<b>Country:</b> {row['Country']}<br>"
                f"<b>City:</b> {row['City']}<br>"
                f"<b>Cluster:</b> <span style='color:{cluster_colors[row['cluster']]};'>cluster {row['cluster']}</span> "
                f"({cluster_descriptions[row['cluster']]})<br>"
                f"<b>AQI Value:</b> {row['AQI Value']}<br>"
                f"<b>CO AQI Value:</b> {row['CO AQI Value']}<br>"
                f"<b>Ozone AQI Value:</b> {row['Ozone AQI Value']}<br>"
                f"<b>NO2 AQI Value:</b> {row['NO2 AQI Value']}<br>"
                f"<b>PM2.5 AQI Value:</b> {row['PM2.5 AQI Value']}"
            )

            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=row['City'],
                icon=icon
            ).add_to(m)
    
    # Display map as HTML
    st.components.v1.html(m._repr_html_(), height=500, scrolling=True)

else:
    # Search city
    search_city = st.text_input("Cari Kota", "")

    # Filter dataframe based on searched city (supporting multiple words)
    if search_city:
        city_data = filtered_df[filtered_df['City'].str.fullmatch(search_city, case=False)]
    else:
        city_data = pd.DataFrame()

    # Display city information
    if not city_data.empty:
        for idx, row in city_data.iterrows():
            cluster = row['cluster']
            color = cluster_colors[cluster]
            description = cluster_descriptions[cluster]
            
            st.markdown(
                f"Kota {row['City']}, {row['Country']}, merupakan Kota yang termasuk ke dalam <span style='color:{color};'>cluster {row['cluster']}</span> "
                f"yang menandakan <span style='color:{color};'>{description}</span>. Berikut adalah detail informasi kota.",
                unsafe_allow_html=True
            )

            # Display warning message based on cluster
            if cluster in cluster_warnings:
                st.markdown(
                    f"<div style='background-color:orange;padding:10px;border-radius:5px;'>"
                    f"{cluster_warnings[cluster]}"
                    f"</div>",
                    unsafe_allow_html=True
                )

            # Create dataframe for table display
            city_info = pd.DataFrame({
                'Negara': [row['Country']],
                'Kota': [row['City']],
                'Cluster': [row['cluster']],
                'AQI Value': [row['AQI Value']],
                'CO AQI Value': [row['CO AQI Value']],
                'Ozone AQI Value': [row['Ozone AQI Value']],
                'NO2 AQI Value': [row['NO2 AQI Value']],
                'PM2.5 AQI Value': [row['PM2.5 AQI Value']]
            })

            # Display table with color highlight
            st.markdown(render_dataframe(city_info, row['cluster'], color), unsafe_allow_html=True)

            st.write("---")  # Separator line between each city entry
    else:
        st.warning("Tidak ada data untuk kota yang dicari.")

    # Create map
    if not city_data.empty:
        m = folium.Map(location=[city_data['Latitude'].mean(), city_data['Longitude'].mean()], zoom_start=12)
        
        # Add markers to map for each city
        for idx, row in city_data.iterrows():
            if 90 >= row['Latitude'] >= -11 and 141 >= row['Longitude'] >= 95:
                if row['cluster'] == 0:
                    icon = folium.Icon(icon='0', prefix='fa', color='blue')
                elif row['cluster'] == 1:
                    icon = folium.Icon(icon='1', prefix='fa', color='orange')
                elif row['cluster'] == 2:
                    icon = folium.Icon(icon='2', prefix='fa', color='red')
                else:
                    icon = folium.Icon(icon='question', prefix='fa', color='gray')

                popup_text = (
                    f"<b>Country:</b> {row['Country']}<br>"
                    f"<b>City:</b> {row['City']}<br>"
                    f"<b>Cluster:</b> <span style='color:{color};'>cluster {row['cluster']}</span> "
                    f"({cluster_descriptions[row['cluster']]})<br>"
                    f"<b>AQI Value:</b> {row['AQI Value']}<br>"
                    f"<b>CO AQI Value:</b> {row['CO AQI Value']}<br>"
                    f"<b>Ozone AQI Value:</b> {row['Ozone AQI Value']}<br>"
                    f"<b>NO2 AQI Value:</b> {row['NO2 AQI Value']}<br>"
                    f"<b>PM2.5 AQI Value:</b> {row['PM2.5 AQI Value']}"
                )

                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=folium.Popup(popup_text, max_width=250),
                    tooltip=row['City'],
                    icon=icon
                ).add_to(m)
        
        # Display map as HTML
        st.components.v1.html(m._repr_html_(), height=500, scrolling=True)
