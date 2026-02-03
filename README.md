# Chemical Visualizer Pro 🧪

**Chemical Visualizer Pro** is a robust, full-stack telemetry dashboard designed to ingest, normalize, and visualize industrial sensor data. It features a unique **Dual-Client Architecture**, offering both a web-based interface (React) and a native desktop application (PyQt5) powered by a single unified Django backend.

The system utilizes a modern **"Vibrant Glass"** design language with real-time dark/light mode switching, **Automated PDF Reporting**, and a **Universal Data Parser** capable of interpreting unstructured datasets without strict schema requirements.

---

## 🚀 Key Features

### 1. Universal Data Ingestion & History 🕒
* **Multi-Format Support:** Upload `.csv`, `.xlsx`, `.xls`, or `.json` files seamlessly.
* **Fuzzy Column Matching:** The backend intelligently scans for keywords like *Temperature* (temp, heat) or *Pressure* (bar, psi) to map data automatically.
* **Smart History Tracking:** Both clients feature a local **Upload History** manager, allowing users to track previous datasets, timestamps, and row counts instantly.

### 2. Advanced Visualization & Reporting 📊
* **"Earth & Ocean" Aesthetics:** Charts utilize a custom professional color palette (Deep Teal, Sage, Sandy Gold, Burnt Orange) to avoid generic AI visuals.
* **Automated PDF Reports:**
    * **Desktop:** Uses `ReportLab` to generate executive summaries and metrics tables.
    * **Web:** Uses `jsPDF` for client-side report generation.
* **Priority Logic:** Algorithms automatically sort metrics by priority (highest values) before visualizing or exporting.

### 3. Integrated Security & Profile Management 🔐
* **Secure Authentication:** A file-based database system (`users.csv`) handles user registration and login.
* **Profile Control:** Users can sign up, update profiles, and perform **secure password changes** (with reuse prevention logic) directly from the client.
* **Admin Console:** A dedicated master view for administrators to manage the user database.

---

## 🛠 Tech Stack

| Module | Technology | Libraries & Tools |
| :--- | :--- | :--- |
| **Backend** | Python 3, Django | `pandas`, `numpy`, `openpyxl`, `django-cors-headers` |
| **Frontend (Web)** | React.js | `chart.js`, `react-chartjs-2`, `axios`, `jspdf`, `jspdf-autotable` |
| **Frontend (Desktop)** | Python, PyQt5 | `matplotlib`, `requests`, `reportlab`, `QStyleSheet` |
| **Data Storage** | SQLite / CSV | Lightweight `users.csv` persistence layer |

---

## ⚙️ Installation & Setup

Follow these steps to run the full ecosystem locally.

### Step 1: Backend Setup (The Brain)
*The backend must be running for the clients to work.*

```bash
# 1. Navigate to the backend folder
cd backend

# 2. Create and activate virtual environment (Optional)
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# 3. Install dependencies
pip install django djangorestframework django-cors-headers pandas openpyxl

# 4. Start the server
python manage.py runserver
```

### Step 2: Desktop Client (PyQt5)
*Ensure you install the new PDF generation library.*
```bash
cd frontend-desktop

# Install GUI and Reporting dependencies
pip install PyQt5 requests matplotlib reportlab

# Launch the App
python main.py
```

### Step 3: Web Client (React)
*Includes the new PDF and Charting libraries.*

```Bash
cd frontend-web

# Install React dependencies
npm install axios chart.js react-chartjs-2 jspdf jspdf-autotable

# Start the Development Server
npm start


