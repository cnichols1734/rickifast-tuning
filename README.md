# Rickifast Tuning CRM

A professional client management and invoicing application for Rickifast Tuning LLC - a performance automotive tuning business.

## Features

- **Client Management**: Track customer contact info and vehicle details
- **Invoice Creation**: Generate professional invoices with line items and tax calculation
- **Payment Tracking**: Record and track payments against invoices
- **Dashboard**: Overview of revenue, outstanding balances, and recent activity
- **Modern UI**: Clean, professional design optimized for automotive business

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Tailwind CSS, Alpine.js
- **Database**: Supabase (PostgreSQL)
- **Hosting**: Railway (production-ready)

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/cnichols1734/rickifast-tuning
cd rickifast-tuning
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Copy `.env.example` to `.env` and fill in your Supabase credentials:
```bash
cp .env.example .env
```

Edit `.env` with your Supabase details:
- `DATABASE_URL`: Your Supabase PostgreSQL connection string
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anon key
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key

### 5. Initialize the database
```bash
python migrate_to_supabase.py
```

### 6. Create an admin user
```bash
python create_admin.py
```

### 7. Run the application
```bash
python app.py
```

The app will be available at `http://localhost:5007`

## Production Deployment (Railway)

1. **Connect your GitHub repository** to Railway
2. **Set environment variables** in Railway dashboard:
   - `DATABASE_URL`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SECRET_KEY` (generate a secure random key)
   - `TAX_RATE` (e.g., 0.0825 for 8.25%)

3. **Deploy**: Railway will automatically deploy when you push to GitHub

## Database

This application uses **Supabase** (PostgreSQL) for both development and production, ensuring consistency across environments. The same database is used for dev and prod.

### Tables
- `user` - Application users
- `client` - Customer records with vehicle information
- `invoice` - Invoices with status tracking
- `invoice_item` - Line items for each invoice
- `payment` - Payment records linked to invoices

## License

This project is licensed under the MIT License.
 