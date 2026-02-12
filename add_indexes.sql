-- =============================================================
-- Supabase Performance Indexes for Rickifast Tuning CRM
-- Run this in Supabase SQL Editor (Dashboard > SQL Editor > New Query)
-- Safe to run multiple times (IF NOT EXISTS)
-- =============================================================

-- Client table
CREATE INDEX IF NOT EXISTS ix_client_last_name   ON client (last_name);
CREATE INDEX IF NOT EXISTS ix_client_email        ON client (email);
CREATE INDEX IF NOT EXISTS ix_client_created_at   ON client (created_at DESC);

-- Invoice table
CREATE INDEX IF NOT EXISTS ix_invoice_client_id   ON invoice (client_id);
CREATE INDEX IF NOT EXISTS ix_invoice_status      ON invoice (status);
CREATE INDEX IF NOT EXISTS ix_invoice_created_at  ON invoice (created_at DESC);
CREATE INDEX IF NOT EXISTS ix_invoice_due_date    ON invoice (due_date);

-- Invoice Item table
CREATE INDEX IF NOT EXISTS ix_invoice_item_invoice_id ON invoice_item (invoice_id);

-- Payment table
CREATE INDEX IF NOT EXISTS ix_payment_invoice_id   ON payment (invoice_id);
CREATE INDEX IF NOT EXISTS ix_payment_payment_date ON payment (payment_date DESC);
CREATE INDEX IF NOT EXISTS ix_payment_method       ON payment (method);
CREATE INDEX IF NOT EXISTS ix_payment_created_at   ON payment (created_at DESC);

-- Composite: payments by date range (dashboard monthly revenue query)
CREATE INDEX IF NOT EXISTS ix_payment_date_amount ON payment (payment_date, amount);
