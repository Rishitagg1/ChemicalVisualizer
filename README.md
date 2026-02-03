# Chemical Visualizer

**Chemical Visualizer** is a robust, full-stack telemetry dashboard designed to ingest, normalize, and visualize industrial sensor data. It features a unique **Dual-Client Architecture**, offering both a web-based interface (React) and a native desktop application (PyQt5) powered by a single unified Django backend.

The system utilizes a custom **Skeuomorphic (Neumorphic)** design language with real-time dark/light mode switching and includes a **Universal Data Parser** capable of interpreting unstructured datasets without strict schema requirements.

---

## 🚀 Key Features

### 1. Universal Data Ingestion
* **Multi-Format Support:** Upload `.csv`, `.xlsx`, `.xls`, or `.json` files.
* **Fuzzy Column Matching:** The backend intelligently scans for keywords like *Temperature* (temp, heat, deg) or *Pressure* (bar, psi, press) to map data automatically.
* **Dynamic Metrics:** The dashboard auto-scales to generate stat cards for *any* numeric column found in the dataset, not just pre-defined ones.

### 2. Advanced UI/UX Design
* **Skeuomorphic Interface:** A "Soft UI" design that mimics physical buttons and inset screens for a tactile feel.
* **Theme Synchronization:** Instant toggle between **Day Mode** (Soft Grey) and **Night Mode** (Deep Charcoal) across all components.
* **Responsive Charts:** Integrated `Chart.js` (Web) and `Matplotlib` (Desktop) for visualizing categorical equipment distributions.

### 3. Integrated Authentication
* **CSV persistence:** A lightweight, file-based database system (`users.csv`) handles user registration and login.
* **Profile Management:** Users can sign up, log in, and update their profiles (Name, Institute, Phone) directly from the client.

---

## 🛠 Tech Stack

| Module | Technology | Libraries & Tools |
| :--- | :--- | :--- |
| **Backend** | Python 3, Django | `pandas`, `numpy`, `openpyxl`, `django-cors-headers` |
| **Frontend (Web)** | React.js | `chart.js`, `react-chartjs-2`, `axios`, `css-variables` |
| **Frontend (Desktop)** | Python, PyQt5 | `matplotlib`, `requests`, `QStyleSheet` |

---

## ⚙️ Installation & Setup

Follow these steps to run the full system locally.

### Step 1: Backend Setup (The Brain)
*The backend must be running for the clients to work.*

```bash
# 1. Navigate to the backend folder
cd backend

# 2. Create and activate virtual environment (Optional but recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install django pandas openpyxl djangocorsheaders

# 4. Start the server
python manage.py runserver
