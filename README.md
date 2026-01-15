# Aqua Force CRM

A simple client management, invoice, and quote web application for Aqua Force Pressure Washing company.

## Features

- Client management
- Quote creation and management
- Invoice creation and management
- Convert quotes to invoices
- Email quotes and invoices to clients
- Dashboard with key metrics

## Tech Stack

- Backend: Flask
- Frontend: HTML, Tailwind CSS, Alpine.js
- Database: SQLite
- Hosting: PythonAnywhere

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cnichols1734/pressure_washing_crm
   cd pressure_washing_crm
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database** (if starting fresh):
   ```bash
   python init_db.py
   ```
   *Note: This repository includes a pre-initialized `aquaforce.db` with sample data.*

5. **Run the application**:
   ```bash
   python run.py
   ```

## Admin Credentials

To log in for the first time, use the following credentials:
- **Username**: `admin`
- **Password**: `adminpassword`

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Tailwind CSS & Bootstrap
- **Database**: SQLite

## Features

- **Client Management**: Track customer details and history.
- **Quote System**: Create professional quotes and send them via email.
- **Invoicing**: Generate invoices and track payment status.
- **Dashboard**: High-level overview of business metrics.

## Deployment

This app is ready to be deployed to **PythonAnywhere** or any other WSGI-compliant hosting provider. Remember to set your `SECRET_KEY` in the environment variables.

## License

This project is licensed under the MIT License.
 