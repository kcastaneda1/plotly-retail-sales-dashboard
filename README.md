# 📊 Retail Sales Dashboard

## 📌 Overview

This project is an interactive **business intelligence dashboard** built using Python and Plotly Dash. It analyzes retail sales data to provide insights into revenue trends, store performance, and product-level analytics.

The dashboard is designed to simulate a real-world analytics tool used by business stakeholders.

---

## 🚀 Features

* 📈 **Sales Trend Analysis** (Time Series)
* 🏪 **Store Performance Comparison**
* 🧩 **Dynamic Filtering**

  * Store selection
  * Item selection
  * Date range filtering
  * Predefined time filters (30D, 60D, 90D, 1Y)
* 📊 **KPI Metrics**

  * Total Sales
  * Average Sales
  * Store Count
  * Top Performing Store
* 📉 **7-Day Rolling Average**
* 📋 **Summary Table with Ranking**

---

## 🛠️ Tech Stack

* Python
* Dash (Plotly)
* Pandas
* NumPy
* Gunicorn (for production)

---

## 📂 Project Structure

```
plotly-retail-dashboard/
│
├── app.py
├── requirements.txt
├── Procfile
├── data/
│   └── retail_sales.csv
└── README.md
```

---

## ⚙️ Installation (Local)

```bash
git clone https://github.com/kcastaneda1/plotly-retail-sales-dashboard.git
cd plotly-retail-sales-dashboard
pip install -r requirements.txt
python app.py
```

---

## 🌐 Live Demo

👉 (Add your Render URL here after deployment)

---

## 📊 Business Value

This dashboard helps answer key business questions:

* Which stores generate the most revenue?
* How do sales trends change over time?
* What are the top-performing products?
* How does performance vary across time periods?

---

## 📸 Screenshots

(Add screenshots here after deployment)

---

## 🧠 Future Improvements

* Add database integration (PostgreSQL / Snowflake)
* Implement user authentication
* Optimize performance with caching
* Enhance UI/UX for enterprise-level design

---

## 📄 License

This project is licensed under the MIT License.
