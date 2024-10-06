import streamlit as st
import requests as r
import pandas as pd
import geocoder
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
from datetime import datetime
from io import StringIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def create_bbox(lat, long, offset=0.2):
    bbox = [long - offset, lat - offset, long + offset, lat + offset]
    return bbox

# Function to query Landsat data from the STAC API
def query_landsat_data(lat, long, date):
    bbox = create_bbox(lat, long)
    params = {
        'limit': 100,  # Number of results
        'bbox': bbox,
        'datetime': f'{date}T00:00:00Z/{date}T23:59:59Z',  # Specific date for query
        'collections': ['landsat-c2l2-sr', 'landsat-c2l2-st'],
        'query': {
            'eo:cloud_cover': {'gte': 0, 'lt': 60},
            'platform': {'in': ['LANDSAT_8', 'LANDSAT_9']}
        }
    }

    # Send the API request
    response = r.post('https://landsatlook.usgs.gov/stac-server/search', json=params)

    # Check for valid response
    if response.status_code == 200:
        query = response.json()
        assets_list = []
        # Parse the response for assets
        for feature in query.get('features', []):
            for asset in feature['assets'].values():
                assets_list.append({
                    'Title': asset['title'],
                    'URL': asset['href']
                })
        
        # Convert to a DataFrame
        if assets_list:
            return pd.DataFrame(assets_list)
        else:
            return "No data found for the given location."
    else:
        st.write(f"Error: {response.status_code}, {response.text}")
        return None

# Function to get the last visit date from NASA API
def get_recent_landsat_overpass(lat, lon):
    url = f"https://api.nasa.gov/planetary/earth/assets?lon={lon}&lat={lat}&dim=0.1&api_key=DEMO_KEY"
    response = r.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'date' in data:
            recent_date = data['date']
            try:
                # Handle the case where there is no 'Z' at the end of the timestamp
                recent_date_obj = datetime.strptime(recent_date, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                # If parsing fails, try without microseconds
                recent_date_obj = datetime.strptime(recent_date, '%Y-%m-%dT%H:%M:%S')
            return recent_date_obj.strftime('%Y-%m-%d')  # Return date in 'YYYY-MM-DD' format
        else:
            return "No recent data available."
    else:
        st.write(f"Error fetching data: {response.status_code}")
        return None

# Function to get coordinates from location name
def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Function to send email with Landsat data
def send_email(email_address, csv_content, last_visit_date):
    # Email setup
    sender_email = "jaswanthjogi7815@gmail.com"  # Your email address
    sender_password = "uiwzwztkowxcnncu"  # Your email password (use app password if needed)
    subject = "Landsat Data and Next Overpass Date"
    body = f"Attached is the Landsat data you requested.\n\nNext Landsat Passover Date: {last_visit_date}"

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_address
    msg['Subject'] = subject

    # Attach the body with the email
    msg.attach(MIMEText(body, 'plain'))

    # Create CSV attachment
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(csv_content)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename="landsat_data.csv"')
    msg.attach(attachment)

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Change to your SMTP server
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.write(f"Failed to send email: {e}")
        return False

# Streamlit interface
st.title("Landsat Data Viewer")

# Create two columns: left for the map and right for inputs
col1, col2 = st.columns([1.4, 3])

# Initialize latitude and longitude variables
latitude, longitude = None, None
data = None  # Initialize data variable

# Persistent map on the left (col1)
with col2:
    #st.write("Click on the map to select a location.")
    
    # Center the map to a default location
    map_center = [20.5937, 78.9629]  # Default center
    m = folium.Map(location=map_center, zoom_start=5)
    
    # Add a marker that will be updated when the user clicks on the map
    map_data = st_folium(m, width=700, height=350)

    # Check if the map was clicked and update the coordinates
    if map_data and map_data.get('last_clicked'):
        latitude, longitude = map_data['last_clicked']['lat'], map_data['last_clicked']['lng']
        st.write(f"Selected Coordinates: Latitude = {latitude}, Longitude = {longitude}")

# Input section on the right (col2)
with col1:
    st.subheader("Input Location Details")

    # Input method selection
    input_method = st.radio("Choose how to input the location:", 
                            ("Enter Coordinates", "Type Location Name", "Auto Fetch User Location"))

    # Input methods
    if input_method == "Enter Coordinates":
        latitude = st.number_input('Latitude', value=latitude or 45.3, format="%.6f")
        longitude = st.number_input('Longitude', value=longitude or -97.4, format="%.6f")

    elif input_method == "Type Location Name":
        location_name = st.text_input("Location Name (e.g., 'New York City')")
        if st.button("Get Coordinates"):
            latitude, longitude = get_coordinates(location_name)
            if latitude and longitude:
                st.write(f"Coordinates for {location_name}: Latitude = {latitude}, Longitude = {longitude}")
            else:
                st.write("Location not found. Please enter a valid location name.")

    elif input_method == "Auto Fetch User Location":
        g = geocoder.ip('me')
        if g.ok:
            latitude, longitude = g.latlng
            st.write(f"Auto-Fetched Coordinates: Latitude = {latitude}, Longitude = {longitude}")
        else:
            st.write("Unable to fetch user location. Please try another method.")

# When the user clicks the button, get the last visit date and then query Landsat data
if latitude is not None and longitude is not None:
    if st.button('Get Last Visit Date'):
        last_visit_date = get_recent_landsat_overpass(latitude, longitude)
        if last_visit_date:
            st.write(f"Last Visit Date for location (Lat: {latitude}, Lon: {longitude}): {last_visit_date}")

            # Now query the Landsat data for that specific date
            data = query_landsat_data(latitude, longitude, last_visit_date)

            # Display the results
            if isinstance(data, pd.DataFrame):
                # Use an expander to display the links in a dropdown-style menu
                with st.expander("Click here to view and download data"):
                    st.write("Click on the titles below to download data:")
                    for index, row in data.iterrows():
                        title = row['Title']
                        url = row['URL']
                        # Create clickable link for each title
                        st.markdown(f"[{title}]({url})", unsafe_allow_html=True)
            else:
                st.write(data)  # Display any error or no data found message
        else:
            st.write("Could not retrieve last visit date.")
            
last_visit_date = get_recent_landsat_overpass(latitude, longitude)
data = query_landsat_data(latitude, longitude, last_visit_date)
# Option to send data via email
email_address = st.text_input("Enter your email address:")
if st.button("Send Data to Email"):
    if data is not None and not data.empty:  # Check if data has been fetched
        # Create CSV content
        csv_buffer = StringIO()
        data.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()

        # Start sending email
        if send_email(email_address, csv_content, last_visit_date):
            st.success("Data sent successfully!")
        else:
            st.error("Failed to send email.")
    else:
        st.warning("No data available to send. Please fetch Landsat data first.")
