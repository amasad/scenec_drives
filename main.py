import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import os

# Load the scenic drives data
@st.cache_data
def load_data():
    return pd.read_csv('data/scenic_drives.csv')

# Create a map centered on the Bay Area
def create_map(data):
    m = folium.Map(location=[37.7749, -122.4194], zoom_start=9)
    
    for _, row in data.iterrows():
        folium.PolyLine(
            locations=eval(row['coordinates']),
            color=row['color'],
            weight=5,
            tooltip=row['name']
        ).add_to(m)
        
        # Add custom marker at the start of each route
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'car_icon.svg')
        custom_icon = folium.CustomIcon(icon_image=icon_path, icon_size=(30, 30))
        folium.Marker(
            eval(row['coordinates'])[0],
            icon=custom_icon,
            popup=folium.Popup(f"<div style='background-color: rgba(255, 255, 255, 0.8); padding: 10px; border-radius: 5px;'><b>{row['name']}</b><br>Length: {row['length']} miles<br>Est. Time: {row['estimated_time']}</div>", max_width=300),
        ).add_to(m)
    
    return m

# Main application
def main():
    st.title("Scenic Drives in the Bay Area")
    
    # Load data
    data = load_data()
    
    # Sidebar
    st.sidebar.title("Scenic Drives")
    selected_drive = st.sidebar.selectbox("Select a drive", data['name'])
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Interactive Map")
        m = create_map(data)
        folium_static(m)
    
    with col2:
        st.subheader("Drive Information")
        drive_info = data[data['name'] == selected_drive].iloc[0]
        st.write(f"**Name:** {drive_info['name']}")
        st.write(f"**Length:** {drive_info['length']} miles")
        st.write(f"**Estimated Time:** {drive_info['estimated_time']}")
        st.write(f"**Description:** {drive_info['description']}")
    
    # List view of all scenic drives
    st.subheader("All Scenic Drives")
    st.table(data[['name', 'length', 'estimated_time']])

if __name__ == "__main__":
    main()
