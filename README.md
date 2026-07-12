# ⚡ EnergiaCerta

> A modern desktop application for **residential solar energy monitoring and management**, built with **Python** and **PySide6 (Qt)**.

EnergiaCerta is a desktop dashboard designed to monitor residential energy generation and consumption in real time. The application supports both **simulation mode** and **Arduino integration**, providing an intuitive interface for energy monitoring, battery management, historical analysis, and automated load management.

---

## 📸 Screenshots

### Dashboard

<p align="center">
  <img width="1523" height="915" alt="image" src="https://github.com/user-attachments/assets/4c43a482-7d31-4c6f-a349-deaccd7e10d8" />

</p>

---

### Critical Loads

<p align="center">
  <img width="1550" height="927" alt="image" src="https://github.com/user-attachments/assets/e3d3c8c3-62a2-4a70-aa07-610a841d6dc4" />

</p>

---

### Battery Monitoring

<p align="center">
  <img width="1537" height="930" alt="image" src="https://github.com/user-attachments/assets/93c6a600-75ff-4e0b-9e41-749b6a6b6a07" />

</p>

---

### Performance Charts

<p align="center">
  <img width="1542" height="930" alt="image" src="https://github.com/user-attachments/assets/0acb0598-77f6-43a5-9976-e451bd469304" />

</p>

---

### Recommendations

<p align="center">
  <img width="1545" height="922" alt="image" src="https://github.com/user-attachments/assets/8ae5e626-29c5-44e9-b2c9-8b1f12b7d37e" />

</p>

---

## ✨ Features

- Real-time dashboard for energy generation and consumption
- Critical and non-critical load management
- Battery monitoring (Voltage, Current, Temperature and State of Charge)
- Historical performance charts
- Automated load management algorithm
- Arduino serial communication support
- Simulation mode for development and testing
- JSON-based local data persistence

---

## 🛠️ Tech Stack

| Category | Technologies |
|-----------|--------------|
| Language | Python |
| GUI | PySide6 (Qt for Python) |
| Data Visualization | Matplotlib |
| Hardware Integration | Arduino + PySerial |
| Storage | JSON |
| Version Control | Git & GitHub |

---

## 📂 Project Structure

```text
EnergiaCerta/
│
├── Main.py
├── leitor.py
├── cargas_db.json
├── historico_energia_db.json
│
├── Core/
│   ├── banco_dados.py
│   ├── comunicacao_serial.py
│   └── simulador.py
│
└── Interface/
    ├── dashboard.py
    ├── abas/
    ├── componentes/
    └── assets/
```

---

## 🚀 Getting Started

Clone the repository

```bash
git clone https://github.com/arthur-afonso-GIT/EnergiaCerta.git
```

Enter the project folder

```bash
cd EnergiaCerta
```

Install the dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python Main.py
```

---

## 🔌 Arduino Integration

The application runs in **Simulation Mode** by default, generating realistic energy production and consumption data without requiring external hardware.

To use a real Arduino:

1. Connect the board via USB.
2. Configure the correct serial port (`COM3`, `COM8`, etc.).
3. Enable hardware mode in the configuration.
4. Upload firmware capable of sending current measurements over the serial connection.

When a new physical load is detected, EnergiaCerta allows the user to register it directly from the interface.

---

## ⚙️ Automated Load Management

EnergiaCerta continuously evaluates the relationship between energy generation, consumption, and battery status.

When an energy deficit is detected, the system automatically disconnects non-critical loads based on their priority and power consumption. Once sufficient energy becomes available again, disconnected loads are restored automatically following the configured priority order.

---

## 💾 Data Persistence

The application stores all local information using JSON files.

| File | Description |
|------|-------------|
| `cargas_db.json` | Registered loads and configuration |
| `historico_energia_db.json` | Energy generation and consumption history |

---

## 🎯 Project Goals

EnergiaCerta was developed to demonstrate the implementation of a complete desktop application that combines graphical interfaces, hardware communication, real-time monitoring, data visualization, and energy management concepts.

The project emphasizes modular software architecture, clean code organization, and integration between software and embedded systems.

---

## 🚧 Future Improvements

- User authentication
- Cloud synchronization
- PostgreSQL support
- Advanced analytics dashboard
- Energy consumption forecasting
- Export reports (PDF/Excel)
- Mobile companion application

---

## 👨‍💻 Author

**Arthur Florêncio Afonso**

- LinkedIn: https://www.linkedin.com/in/arthur-flor%C3%AAncio-afonso/
- GitHub: https://github.com/arthur-afonso-GIT
