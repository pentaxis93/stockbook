-- StockBook Database Schema
-- SQLite3 compatible

-- Stock information
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    industry_group TEXT,
    grade TEXT CHECK(grade IN ('A', 'B', 'C', NULL)),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio accounts
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    max_positions INTEGER DEFAULT 10,
    max_risk_per_trade DECIMAL(3,1) DEFAULT 2.0, -- percentage
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Watchlist/Target stocks
CREATE TABLE IF NOT EXISTS target (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    portfolio_id INTEGER NOT NULL,
    pivot_price DECIMAL(10,2) NOT NULL,
    failure_price DECIMAL(10,2) NOT NULL,
    notes TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'hit', 'failed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stock(id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id)
);

-- Buy/Sell transactions
CREATE TABLE IF NOT EXISTS stock_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('buy', 'sell')),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    transaction_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
    FOREIGN KEY (stock_id) REFERENCES stock(id)
);

-- Portfolio balance history
CREATE TABLE IF NOT EXISTS portfolio_balance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    balance_date DATE NOT NULL,
    withdrawals DECIMAL(12,2) DEFAULT 0,
    deposits DECIMAL(12,2) DEFAULT 0,
    final_balance DECIMAL(12,2) NOT NULL,
    index_change DECIMAL(5,2), -- percentage change of benchmark index
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
    UNIQUE(portfolio_id, balance_date)
);

-- Trading journal
CREATE TABLE IF NOT EXISTS journal_entry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date DATE NOT NULL,
    content TEXT NOT NULL,
    stock_id INTEGER,
    portfolio_id INTEGER,
    transaction_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stock(id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
    FOREIGN KEY (transaction_id) REFERENCES stock_transaction(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_transaction_portfolio ON stock_transaction(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_transaction_stock ON stock_transaction(stock_id);
CREATE INDEX IF NOT EXISTS idx_transaction_date ON stock_transaction(transaction_date);
CREATE INDEX IF NOT EXISTS idx_target_status ON target(status);
CREATE INDEX IF NOT EXISTS idx_portfolio_balance_date ON portfolio_balance(balance_date);
CREATE INDEX IF NOT EXISTS idx_journal_entry_date ON journal_entry(entry_date);

-- Trigger to update timestamps
CREATE TRIGGER IF NOT EXISTS update_stock_timestamp
AFTER UPDATE ON stock
BEGIN
    UPDATE stock SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_portfolio_timestamp
AFTER UPDATE ON portfolio
BEGIN
    UPDATE portfolio SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_target_timestamp
AFTER UPDATE ON target
BEGIN
    UPDATE target SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_journal_entry_timestamp
AFTER UPDATE ON journal_entry
BEGIN
    UPDATE journal_entry SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
