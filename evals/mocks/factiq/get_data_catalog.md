{
  "schemas": [
    {
      "schema": "bls",
      "organization": "Bureau of Labor Statistics",
      "country": "USA"
    },
    {
      "schema": "oews",
      "organization": "Bureau of Labor Statistics",
      "country": "USA"
    },
    {
      "schema": "census",
      "organization": "Census Bureau",
      "country": "USA"
    },
    {
      "schema": "bea",
      "organization": "Bureau of Economic Analysis",
      "country": "USA"
    },
    {
      "schema": "eia",
      "organization": "Energy Information Administration",
      "country": "USA"
    },
    {
      "schema": "ers",
      "organization": "Economic Research Service (USDA)",
      "country": "USA"
    },
    {
      "schema": "bts",
      "organization": "Bureau of Transportation Statistics",
      "country": "USA"
    },
    {
      "schema": "frb",
      "organization": "Federal Reserve Board",
      "country": "USA"
    },
    {
      "schema": "treasury",
      "organization": "U.S. Department of the Treasury",
      "country": "USA"
    },
    {
      "schema": "ui_claims",
      "organization": "Department of Labor, Employment & Training Administration",
      "country": "USA"
    },
    {
      "schema": "china",
      "organization": "National Bureau of Statistics of China",
      "country": "China"
    },
    {
      "schema": "mospi",
      "organization": "Ministry of Statistics and Programme Implementation India",
      "country": "India"
    },
    {
      "schema": "rbi",
      "organization": "Reserve Bank of India",
      "country": "India"
    },
    {
      "schema": "imf",
      "organization": "International Monetary Fund",
      "country": "Global"
    },
    {
      "schema": "worldbank",
      "organization": "World Bank",
      "country": "Global"
    },
    {
      "schema": "singstat",
      "organization": "Singapore Department of Statistics",
      "country": "Singapore"
    },
    {
      "schema": "china_customs",
      "organization": "General Administration of Customs of China",
      "country": "China"
    },
    {
      "schema": "india_trade",
      "organization": "Directorate General of Commercial Intelligence and Statistics (DGCI&S)",
      "country": "India"
    },
    {
      "schema": "korea_trade",
      "organization": "Korea Customs Service (KCS)",
      "country": "South Korea"
    },
    {
      "schema": "japan_trade",
      "organization": "Japan Customs / Ministry of Finance",
      "country": "Japan"
    },
    {
      "schema": "taiwan_trade",
      "organization": "International Trade Administration (ITA), Ministry of Economic Affairs (Taiwan)",
      "country": "Taiwan"
    },
    {
      "schema": "eu_comext_de",
      "organization": "Eurostat Comext",
      "country": "Germany"
    },
    {
      "schema": "eu_comext_fr",
      "organization": "Eurostat Comext",
      "country": "France"
    },
    {
      "schema": "eu_comext_nl",
      "organization": "Eurostat Comext",
      "country": "Netherlands"
    },
    {
      "schema": "portwatch",
      "organization": "IMF PortWatch (satellite-AIS shipping data)",
      "country": "Global"
    },
    {
      "schema": "satellite",
      "organization": "NASA Black Marble & satellite-derived indicators",
      "country": "Global"
    },
    {
      "schema": "nasa_fires",
      "organization": "NASA FIRMS (VIIRS active fire detections)",
      "country": "Global"
    },
    {
      "schema": "eu",
      "organization": "EU institutions (Eurostat, ECB, EEA, and EU ETS)",
      "country": "Europe"
    },
    {
      "schema": "uk",
      "organization": "UK official statistics (ONS, Bank of England, DEFRA, HMRC, DBT, and DfT)",
      "country": "United Kingdom"
    }
  ],
  "schemas_without_data": [
    "ir"
  ],
  "mode": "compact",
  "dataset_descriptions": "Available data schemas (one source each). To find the right dataset, call `search_datasets` with keywords (it ranks datasets across all schemas), then `describe_dataset` for full detail on one. Discover individual series with `run_sql` on the `series` and `dimensions` tables.\n\n- `bls` (Bureau of Labor Statistics; USA; 32 datasets): US labor & prices: employment, unemployment, CPI inflation, wages/earnings, JOLTS job openings & turnover, producer prices (PPI), import/export prices, productivity.\n- `bea` (Bureau of Economic Analysis; USA; 9 datasets): US national accounts: GDP and components, personal income & outlays, PCE inflation, trade, industry value added.\n- `census` (Census Bureau; USA; 40 datasets): US business, retail, construction, trade and demographic programs.\n- `china_customs`, `india_trade`, `korea_trade`, `japan_trade`, `taiwan_trade`, `eu_comext_*`: bilateral merchandise trade by HS commodity code and partner.\n\n## Financial Market Data\nUse `get_market_data` for live stock prices, commodity futures, forex rates, company profiles, and ETF profiles.\n\n**For US/global economic indicators (GDP, CPI, unemployment, federal funds rate, retail sales, nonfarm payrolls), use the database via `run_sql` or `get_series`.**\n",
  "db_schema": "CREATE TABLE IF NOT EXISTS series (\n    id SERIAL PRIMARY KEY,\n    dataset_code VARCHAR(50) NOT NULL,\n    series_id VARCHAR(100) NOT NULL UNIQUE,\n    series_title TEXT,\n    human_friendly_title TEXT,\n    human_friendly_description TEXT,\n    measurement_units TEXT,\n    frequency TEXT,\n    adjusted_for_seasonality BOOLEAN,\n    state TEXT,\n    county_or_metro_area TEXT,\n    begin_time TIMESTAMP,\n    end_time TIMESTAMP,\n    footnote_codes TEXT,\n    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n    data_type VARCHAR(20) NOT NULL DEFAULT 'timeseries',\n    tabular_columns JSONB\n);\n\nCREATE TABLE IF NOT EXISTS data_points (\n    series_id VARCHAR(100) NOT NULL,\n    time TIMESTAMP NOT NULL,\n    value DOUBLE PRECISION,\n    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);\nCREATE INDEX IF NOT EXISTS data_points_series_id_time_idx ON data_points (series_id, \"time\" DESC);\n\nCREATE TABLE IF NOT EXISTS tabular_data (\n    series_id VARCHAR(100) NOT NULL,\n    row_index INTEGER NOT NULL,\n    row_data JSONB NOT NULL,\n    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n    PRIMARY KEY (series_id, row_index)\n);\n\nCREATE TABLE IF NOT EXISTS dimensions (\n    id SERIAL PRIMARY KEY,\n    series_id VARCHAR(100) NOT NULL,\n    dimension_type VARCHAR(255) NOT NULL,\n    dimension_code VARCHAR(1024),\n    dimension_name TEXT\n);\n\nCREATE TABLE IF NOT EXISTS compound_series (\n    id SERIAL PRIMARY KEY,\n    series_id VARCHAR NOT NULL UNIQUE,\n    dataset_code VARCHAR(50) NOT NULL,\n    title TEXT NOT NULL,\n    description TEXT,\n    sql_template TEXT NOT NULL,\n    member_series_pattern TEXT,\n    is_active BOOLEAN DEFAULT TRUE,\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);\n"
}
