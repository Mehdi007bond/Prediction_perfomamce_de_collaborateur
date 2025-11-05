# HR Forecasting Web Application

## Description

This project is a web-based HR forecasting application built with Flask. It predicts employee performance using a machine learning model and presents the insights through an interactive dashboard. The application generates its own dummy data for demonstration purposes, trains a RandomForest Regressor model, and visualizes historical data, future predictions, and key performance indicators.

## Features

- **Interactive Dashboard:** A user-friendly web interface to visualize HR data and predictions.
- **Machine Learning Model:** Utilizes a `RandomForestRegressor` from scikit-learn to predict future employee performance.
- **Data Visualization:** Presents data through various charts and tables, including:
  - Historical performance data.
  - Future predictions with confidence intervals.
  - Key Performance Indicators (KPIs) such as current average score, 7-day prediction, and performance trends.
  - Key influencers on performance.
  - Performance breakdown by sector and production line.
  - Top and bottom 5 performing employees.
- **Filtering:** Allows users to filter the data by sector and production line.
- **Customizable Prediction Period:** Users can select the number of days for which they want to see the forecast.
- **Dummy Data Generation:** Includes a comprehensive script to generate realistic dummy data for employees, skills, and evaluations.

## How to Run

1. **Install Dependencies:**
   Make sure you have Python installed. Then, install the required libraries using pip:
   ```bash
   pip install pandas numpy scikit-learn matplotlib flask
   ```

2. **Run the Application:**
   Execute the following command in your terminal:
   ```bash
   python interface_projet_filmod.py
   ```

3. **Access the Dashboard:**
   Open your web browser and navigate to `http://127.0.0.1:5000`.

## Dependencies

- pandas
- numpy
- scikit-learn
- matplotlib
- Flask

## File Structure

- `interface_projet_filmod.py`: The main and only file, containing the entire application logic. It includes:
  - The Flask web server.
  - The HTML/CSS/Jinja2 template for the web interface.
  - The logic for generating dummy data.
  - The machine learning model training and prediction functions.
  - The routes for handling web requests and rendering the dashboard.
