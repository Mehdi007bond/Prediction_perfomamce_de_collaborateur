# 🚀 HR Forecasting Web Application

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931A?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3776AB?style=for-the-badge&logo=matplotlib&logoColor=white)
![Dataset](https://img.shields.io/badge/Dataset-4,050%20samples-brightgreen?style=for-the-badge)

## 📝 Description

This project is a comprehensive, web-based HR forecasting application built with Flask. Its primary goal is to predict employee performance trends using a machine learning model, providing valuable insights to HR professionals and managers through an intuitive and interactive dashboard.

The application simulates a real-world HR environment by generating its own rich, fictional dataset that includes employee information, skill evaluations across different categories (Maintenance, Production, Quality, Method), and historical performance data. This data is then used to train a `RandomForestRegressor` model from the scikit-learn library. The model learns from temporal features and the composition of skills to make accurate predictions about future performance scores.

The dashboard is the core of the application, offering a clean, modern interface for users to explore the data, view predictions, and identify key factors influencing performance. All of this is contained within a single Python script, making it a powerful yet easy-to-deploy tool for HR analytics.

## ✨ Features

-   **Interactive Dashboard:** A user-friendly web interface to visualize HR data and predictions.
-   **Machine Learning Model:** Utilizes a `RandomForestRegressor` from scikit-learn to predict future employee performance.
-   **Data Visualization:** Presents data through various charts and tables, including:
    -   Historical performance data.
    -   Future predictions with confidence intervals.
    -   Key Performance Indicators (KPIs) such as current average score, 7-day prediction, and performance trends.
    -   Key influencers on performance.
    -   Performance breakdown by sector and production line.
    -   Top and bottom 5 performing employees.
-   **Filtering:** Allows users to filter the data by sector and production line.
-   **Customizable Prediction Period:** Users can select the number of days for which they want to see the forecast.
-   **Dummy Data Generation:** Includes a comprehensive script to generate realistic dummy data for employees, skills, and evaluations.

## ⚙️ How to Run

1.  **Install Dependencies:**
    Make sure you have Python installed. Then, install the required libraries using pip:
    ```bash
    pip install pandas numpy scikit-learn matplotlib flask
    ```

2.  **Run the Application:**
    Execute the following command in your terminal:
    ```bash
    python interface_projet_filmod.py
    ```

3.  **Access the Dashboard:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

## 🔬 Function Descriptions

| Function                       | Emoji | Purpose                                                                                                 |
| ------------------------------ | :---: | ------------------------------------------------------------------------------------------------------- |
| `charger_et_nettoyer_donnees()`  |  💾   | Generates, cleans, and merges the fictional data for employees, evaluations, and skills.                |
| `entrainer_modele()`             |  🧠   | Prepares the data and trains the `RandomForestRegressor` model to understand performance patterns.      |
| `predire_rf()`                   |  🔮   | Uses the trained model to generate future performance predictions with confidence intervals.            |
| `generer_barplot_base64()`       |  📊   | Creates various bar plots (e.g., performance by sector) and converts them to Base64 for web display.    |
| `index()`                        |  🌐   | The main Flask route that handles user requests, orchestrates the data processing, and renders the HTML dashboard. |

## 📁 File Structure

-   `interface_projet_filmod.py`: The main and only file, containing the entire application logic. It includes:
    -   The Flask web server.
    -   The HTML/CSS/Jinja2 template for the web interface.
    -   The logic for generating dummy data.
    -   The machine learning model training and prediction functions.
    -   The routes for handling web requests and rendering the dashboard.

## 🏷️ Tags

`#python`, `#flask`, `#machine-learning`, `#data-science`, `#hr`, `#forecasting`, `#data-visualization`
