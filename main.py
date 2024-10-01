import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import psycopg2
import os
from psycopg2.extras import RealDictCursor

# Database connection
def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

# Initialize database
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scenic_drives (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            length FLOAT NOT NULL,
            estimated_time VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            coordinates TEXT NOT NULL,
            color VARCHAR(7) NOT NULL
        )
    """)
    
    # Check if the table is empty
    cur.execute("SELECT COUNT(*) FROM scenic_drives")
    if cur.fetchone()[0] == 0:
        # Insert initial data
        initial_data = [
            ("Pacific Coast Highway", 60, "2 hours 30 minutes", "Stunning coastal drive with breathtaking ocean views", "[[37.4989,-122.5021],[37.2718,-122.4080],[37.0824,-122.2781],[36.9741,-122.0262],[36.9641,-121.9025]]", "#FF5733"),
            ("Skyline Boulevard", 50, "1 hour 45 minutes", "Scenic route along the ridge of the Santa Cruz Mountains", "[[37.5033,-122.3728],[37.3867,-122.3036],[37.2510,-122.1225],[37.1426,-122.1248],[37.0505,-122.0778]]", "#33FF57"),
            ("Mount Tamalpais Scenic Loop", 30, "1 hour 15 minutes", "Winding mountain roads with panoramic views of the Bay Area", "[[37.8969,-122.5825],[37.9235,-122.5962],[37.9131,-122.5736],[37.8881,-122.5736],[37.8969,-122.5825]]", "#3357FF"),
            ("Napa Valley Wine Country Drive", 40, "1 hour 30 minutes", "Picturesque drive through rolling hills and vineyards", "[[38.2975,-122.2869],[38.4065,-122.3644],[38.5075,-122.4597],[38.5788,-122.5847],[38.5788,-122.5847]]", "#FF33F1"),
            ("Berkeley Hills Panoramic Drive", 15, "45 minutes", "Short but scenic drive with stunning Bay views", "[[37.8715,-122.2508],[37.8904,-122.2437],[37.9029,-122.2615],[37.8801,-122.2391],[37.8715,-122.2508]]", "#33FFF1")
        ]
        cur.executemany("""
            INSERT INTO scenic_drives (name, length, estimated_time, description, coordinates, color)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, initial_data)
    
    conn.commit()
    cur.close()
    conn.close()

# Load the scenic drives data
@st.cache_data
def load_data():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM scenic_drives")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(data)

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
        
        # Add marker at the start of each route
        folium.Marker(
            eval(row['coordinates'])[0],
            popup=folium.Popup(f"<div style='background-color: rgba(255, 255, 255, 0.8); padding: 10px; border-radius: 5px;'><b>{row['name']}</b><br>Length: {row['length']} miles<br>Est. Time: {row['estimated_time']}</div>", max_width=300),
        ).add_to(m)
    
    return m

# Main application
def main():
    # Initialize the database
    init_db()

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
