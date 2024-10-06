# NASA Space Apps Challenge 2024 - Noida

### **Team Name**: Moon-Light  
### **Problem Statement**: Landsat Reflectance Data: On the Fly and at Your Fingertips  
### **Team Leader Email**: jaswanthjogi7815@gmail.com

## Project Overview
Our project aims to create a web-based application that allows users to compare ground-based spectral measurements with Landsat Surface Reflectance (SR) data. Users can define a target location through various methods: manual coordinate input, live location detection, place name entry, or selecting a location on an interactive map. Once the location is set, the app offers several functionalities, including:

- Fetching the most recent Landsat data for the chosen location.
- Creating time-series animations for a selected date range.
- Plotting Surface Reflectance (SR) data over time.
- Providing download links for various spectral bands and images directly from the Landsat Look website via an open API.
- Setting up notifications to alert the user when the Landsat satellite passes over the selected location.

These features facilitate seamless access to Landsat data, encouraging scientific exploration and enabling users to easily download and process the relevant datasets.

## Key Features
- **Location Selection**: Choose a target location by entering coordinates, using live location, or selecting a place on the map.
- **Landsat Data Access**: Fetch SR data, spectral bands, and imagery files for a specified location or time period.
- **Time Series Analysis**: Generate animations that show data changes over a defined time span.
- **Cloud Coverage Filter**: Users can set a threshold for cloud coverage to ensure only clear data is returned.
- **Notifications**: Receive alerts when Landsat passes over the defined location.

## Code Execution Instructions

To run the web-based application, follow these steps:

1. Clone this repository using:
   ```bash
   git clone https://github.com/your-repo-url
   ```
2. Install the required dependencies from the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables (e.g., API keys, email configurations) as specified in the `env.sample` file.
4. Run the Streamlit app using:
   ```bash
   streamlit run app.py
   ```
5. Open your browser and navigate to the displayed local URL to access the application.

## Execution Plan
The repository includes a detailed **Execution Plan PDF** which outlines:

- The project objectives.
- The system architecture.
- Our approach to solving the problem statement.
- Workflow and specific technologies used, such as Streamlit for the web interface, Open APIs for data integration, and methods for data notification.

Feel free to explore the PDF for a more in-depth look at how this application operates and the problem-solving techniques involved.
