-- =============================================================================
-- DDL Script: Factoring B2B MVP Schema Definitions
-- Target DB: PostgreSQL 14+ / SQLite
-- =============================================================================

-- 1. Users Table (Legal Representatives & Admins)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    dni VARCHAR(20) UNIQUE NOT NULL,
    phone VARCHAR(30),
    role VARCHAR(50) NOT NULL DEFAULT 'GIRADOR',
    verification_status VARCHAR(50) NOT NULL DEFAULT 'PENDING_VERIFICATION',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    locked_until TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_dni ON users(dni);

-- 2. Companies Table (Corporate Clients / Giradores)
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    ruc VARCHAR(11) UNIQUE NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    legal_representative_user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bank_name VARCHAR(100) NOT NULL,
    bank_account_number VARCHAR(50) NOT NULL,
    cci VARCHAR(20) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'PEN',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_companies_ruc ON companies(ruc);
CREATE INDEX IF NOT EXISTS idx_companies_legal_rep ON companies(legal_representative_user_id);

-- 3. Company Documents Table (Tax / Legal Proofs)
CREATE TABLE IF NOT EXISTS company_documents (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_company_documents_company_id ON company_documents(company_id);

-- 4. User Sessions Table (JWT Active Sessions)
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_jti ON user_sessions(token_jti);

-- 5. Invoice Sheets Table (Factoring Batches / Planillas)
CREATE TABLE IF NOT EXISTS invoice_sheets (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    sheet_code VARCHAR(50) UNIQUE NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'PEN',
    total_amount DOUBLE PRECISION NOT NULL,
    advance_amount DOUBLE PRECISION NOT NULL,
    interest_fee DOUBLE PRECISION NOT NULL,
    commission DOUBLE PRECISION NOT NULL,
    net_disbursement DOUBLE PRECISION NOT NULL,
    advance_rate DOUBLE PRECISION NOT NULL DEFAULT 0.85,
    monthly_rate DOUBLE PRECISION NOT NULL DEFAULT 0.02,
    status VARCHAR(50) NOT NULL DEFAULT 'QUOTED',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_invoice_sheets_company_id ON invoice_sheets(company_id);
CREATE INDEX IF NOT EXISTS idx_invoice_sheets_code ON invoice_sheets(sheet_code);

-- 6. Invoices Table (Individual Negotiable Invoices)
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    sheet_id INTEGER NOT NULL REFERENCES invoice_sheets(id) ON DELETE CASCADE,
    invoice_number VARCHAR(50) NOT NULL,
    drawer_ruc VARCHAR(11) NOT NULL,
    debtor_ruc VARCHAR(11) NOT NULL,
    debtor_name VARCHAR(255) NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    currency VARCHAR(10) NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    days_to_maturity INTEGER NOT NULL,
    sunat_status VARCHAR(20) NOT NULL DEFAULT 'VALID',
    is_approved BOOLEAN NOT NULL DEFAULT TRUE,
    rejection_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_invoices_sheet_id ON invoices(sheet_id);

-- 7. Disbursements Table (Payment Execution & CAVALI Annotations)
CREATE TABLE IF NOT EXISTS disbursements (
    id SERIAL PRIMARY KEY,
    sheet_id INTEGER UNIQUE NOT NULL REFERENCES invoice_sheets(id) ON DELETE CASCADE,
    annotation_code VARCHAR(100) UNIQUE NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'PEN',
    bank_name VARCHAR(100) NOT NULL,
    bank_account_number VARCHAR(50) NOT NULL,
    cci VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'DISBURSED',
    executed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_disbursements_sheet_id ON disbursements(sheet_id);
CREATE INDEX IF NOT EXISTS idx_disbursements_annotation_code ON disbursements(annotation_code);

-- 8. Negotiation Histories Table (Rate Counter-Offers)
CREATE TABLE IF NOT EXISTS negotiation_histories (
    id SERIAL PRIMARY KEY,
    sheet_id INTEGER NOT NULL REFERENCES invoice_sheets(id) ON DELETE CASCADE,
    requested_rate DOUBLE PRECISION NOT NULL,
    offered_rate DOUBLE PRECISION NOT NULL,
    requested_by_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_negotiation_histories_sheet_id ON negotiation_histories(sheet_id);
