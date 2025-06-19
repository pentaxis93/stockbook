# Domain Layer Business Logic Inventory

## Entity: StockEntity

### Attributes:

**symbol: StockSymbol**
Unique identifier for the stock in the trading system. Must follow standard stock ticker format (1-5 uppercase letters). Cannot be changed once created as it serves as the business key.

```
1. Replace this attribute with a new value object named symbol_vo.
2. The stock symbol can be changed, since companies can change their ticker symbol.
```

**company_name: CompanyName**
The official name of the company issuing the stock. Limited to 100 characters and cannot be empty.


```
1. Replace this attribute with a new value object named company_name_vo.
2. The company name can be empty. Users should be able to create a stock by providing only the symbol.
```

**sector_vo: Optional[Sector]**
High-level industry classification of the company (e.g., Technology, Healthcare). Must be one of 11 predefined sectors or None. When set, constrains which industry groups can be assigned.


```
Perfect.
```

**industry_group_vo: Optional[IndustryGroup]**
Specific industry classification within a sector. Must belong to the assigned sector if both are specified. Cannot exist without a sector.


```
Perfect.
```

**grade: Optional[str]**
Investment quality rating assigned to the stock. Must be 'A', 'B', or 'C' if specified. Represents investment desirability or risk level.


```
1. Replace this attribute with a new value object named grade_vo.
2. The grade can be 'A', 'B', 'C', 'D', 'F', or None.
```

**notes_vo: Notes**
Free-form text for additional observations about the stock. Limited to 5000 characters. Used for capturing analyst insights or trading notes.


```
Good. But change the name to stock_notes_vo.
```

**id: Optional[int]**
Database persistence identifier. Once set, cannot be changed. Must be a positive integer.


```
Yes, but id is not optional because it is a primary key.
```

### Methods:

**calculate_position_value(quantity: Quantity, price: Money) -> Money**
Calculates the total market value of a stock position by multiplying shares owned by current price. Used for portfolio valuation and position sizing.


```
Perfect.
```

**has_notes() -> bool**
Checks whether the stock has any meaningful notes content. Returns true only if notes exist and contain non-whitespace characters.


```
Remove this method.
```

**update_fields(**kwargs) -> None**
Updates multiple stock attributes in a single atomic operation. Validates all changes before applying any. If sector changes, automatically clears industry_group if incompatible. Ensures sector-industry relationship integrity is maintained.


```
Good. All the fields will be value objects after the changes recommended above,
so the value objects will provide validation. Sector and industry group can be
given at the same time, and both will be updated as long as the industry group
belongs to the sector. If not, the sector will be updated and the industry group
will be cleared.
```

**set_id(stock_id: int) -> None**
Sets the database identifier for newly persisted stocks. Can only be called once on stocks without an ID. Prevents accidental ID changes that could corrupt data relationships.


```
Remove this method. The id will be set by the database since it is a primary key.
```

**_validate_sector_industry_combination(sector: Optional[str], industry_group: Optional[str]) -> None**
Enforces business rule that industry groups must belong to their assigned sector. Uses SectorIndustryService to validate allowed combinations. Throws ValueError if an invalid pairing is attempted.


```
Perfect.
```

**_validate_grade(grade: Optional[str]) -> None**
Ensures grade is one of the allowed values (A, B, C) or None. Part of the stock quality rating system.


```
Remove this method. It is not needed because grade is a value object.
```

## Entity: PortfolioEntity

### Attributes:

**id: Optional[int]**
Database identifier for the portfolio. Unique across the system.


```
Not optional, this is a primary key.
```

**name: str**
Display name for the portfolio. Cannot be empty and limited to 100 characters. Used to identify and distinguish between multiple portfolios.


```
Replace this with a new value object named portfolio_name_vo.
```

**description: Optional[str]**
Extended description of the portfolio's purpose or strategy. Optional field for additional context.


```
Good, but let's make this a value object named portfolio_notes_vo. It should be a string with maximum
length of 250 characters.
```

**created_date: Optional[date]**
Date when the portfolio was established. Used for historical tracking and performance measurement.


```
1. This should be a shared kernel value object - Date.
2. The date should be changeable.
```

**is_active: bool**
Indicates whether the portfolio is currently in use. Inactive portfolios are retained for historical records but excluded from active trading.


```
Good.
```

### Methods:

**__post_init__() -> None**
Validates portfolio data immediately after creation. Ensures name is provided and within length limits. Enforces basic data integrity rules.


```
Good. But the name should be a value object, which will provide its own validation.
```

## Entity: JournalEntryEntity

### Attributes:

**id: Optional[int]**
Database identifier for the journal entry.


```
Yes - but not optional, because it is a primary key.
```

**portfolio_id: Optional[int]**
Links the journal entry to a specific portfolio. Enables portfolio-specific notes and observations.


```
Yes. This is an optional foreign key, because journal entries can be tied to a
portfolio, or not.
```

**stock_id: Optional[int]**
Links the journal entry to a specific stock. Allows tracking stock-specific research and decisions.


```
Yes. This is an optional foreign key, because journal entries can be tied to a
stock, or not.
```

**transaction_id: Optional[int]**
Links the journal entry to a specific trade. Captures reasoning and context for individual transactions.


```
Yes. This is an optional foreign key, because journal entries can be tied to a
transaction, or not.
```

**entry_date: Optional[date]**
Date of the journal entry. Required field for chronological organization and historical analysis.


```
Instead of just a date, can we make this a time stamp containing the date and time?
It should probably be a shared kernel value object with a name like TimeStamp.
```

**content: str**
The actual journal text. Cannot be empty and limited to 10,000 characters. Contains investment reasoning, market observations, or trade rationale.


```
OK. But make the max length 5000 characters.
```

### Methods:

**__post_init__() -> None**
Validates journal entry upon creation. Ensures content is not empty, date is provided, and content length is within limits. Maintains data quality for investment record keeping.


```
OK, but have value objects do as much validation as possible.
```

## Entity: TransactionEntity

```
We must rename this to OrderEntity. It's not a transaction, it's an order.
This is a change in the domain layer, reflecting newly understood requirements.
```

### Attributes:

**id: Optional[int]**
Database identifier for the transaction.


```
This is a primary key, so it's not optional. It identifies the order, not the
transaction.
```

**portfolio_id: int**
Identifies which portfolio executed this trade. Must be positive. Links transactions to portfolio performance tracking.


```
Yes, this is required for every order. It's a foreign key, so it will follow the
validation rules of the foreign key. It actually reflects the portolio that placed
the order (not executing a trade).
```

**stock_id: int**
Identifies which stock was traded. Must be positive. Essential for position tracking and P&L calculations.


```
Yes, required for every transaction. It isn't really that it has to be positive;
this is a foreign key, so it will follow the rules of the foreign key.
```

**transaction_type: str**
Indicates whether this was a 'buy' or 'sell' transaction. Required field that determines position direction and cash flow.


```
Rename to order_type.
```

**quantity: Optional[Quantity]**
Number of shares traded. Uses Quantity value object for precision and unit consistency.


```
This is required, not optional.
```

**price: Optional[Money]**
Price per share at execution. Uses Money value object for currency handling and arithmetic precision.


```
Replace this with three separate optional price attributes: stop_price, limit_price, and
execution_price.
```

**transaction_date: Optional[date]**
Date when the trade was executed. Critical for historical position reconstruction and tax calculations.


```
Use a time stamp value object instead of just a date. Also this must be replaced
with two separate timestamp fields: order_timestamp (required) and execution_timestamp (optional).
```

**notes: Optional[str]**
Optional text for trade-specific comments. Captures execution details or special circumstances.


```
Remove this field - we will use the journal entry for this.
```

### Methods:

**__post_init__() -> None**
Validates transaction integrity after creation. Ensures transaction type is valid ('buy' or 'sell'), and both portfolio_id and stock_id are positive integers. Prevents invalid trades from entering the system.


```
Yes. But the value objects should do as much validation as possible.
```

## Entity: PortfolioBalanceEntity

### Attributes:

**id: Optional[int]**
Database identifier for the balance record.


```
Not optional, this is a primary key.
```

**portfolio_id: int**
Links balance to specific portfolio. Must be positive. Enables tracking multiple portfolio performances independently.


```
This is the foreign key, required for every balance record.
```

**balance_date: Optional[date]**
Date of the balance snapshot. Required for time-series analysis and performance tracking.


```
Required, not optional.
```

**withdrawals: Optional[Money]**
Cash removed from portfolio during the period. Affects return calculations by adjusting the capital base.


```
Exactly. But let's replace this 'withdrawals' attribue and the 'deposits' attribute
with a single cash_flow attribute.
```

**deposits: Optional[Money]**
Cash added to portfolio during the period. Impacts performance metrics by changing invested capital.


```
See above.
```

**final_balance: Optional[Money]**
Total portfolio value at the balance date. Required field representing sum of all positions plus cash.


```
Yes, but this is required.
```

**index_change: Optional[float]**
Benchmark index performance for the same period as a percentage. Enables relative performance comparison.


```
Replace this with two separate fields: nasdaq_index and sp500_index.
```

### Methods:

**__post_init__() -> None**
Validates balance record completeness. Ensures portfolio_id is positive, balance_date is provided, and final_balance exists. Critical for maintaining accurate performance history.


```
________________________
```

## Entity: TargetEntity

### Attributes:

**id: Optional[int]**
Database identifier for the price target.


```
________________________
```

**portfolio_id: int**
Links target to specific portfolio. Must be positive. Allows portfolio-specific trading strategies.


```
________________________
```

**stock_id: int**
Identifies which stock this target applies to. Must be positive. Essential for trade execution monitoring.


```
________________________
```

**pivot_price: Optional[Money]**
Target price for entering or exiting a position. Required field representing the desired execution level.


```
________________________
```

**failure_price: Optional[Money]**
Stop-loss price to limit downside risk. Required field defining maximum acceptable loss threshold.


```
________________________
```

**status: str**
Current state of the target: 'active' (monitoring), 'hit' (pivot reached), 'failed' (stop triggered), or 'cancelled' (manually closed). Tracks target lifecycle.


```
________________________
```

**created_date: Optional[date]**
Date when target was established. Used for age tracking and historical analysis.


```
________________________
```

**notes: Optional[str]**
Optional commentary about the target rationale. Documents the reasoning behind specific price levels.


```
________________________
```

### Methods:

**__post_init__() -> None**
Validates target configuration at creation. Ensures status is valid, IDs are positive, and both pivot and failure prices are specified. Prevents incomplete or invalid targets from being created.


```
________________________
```
