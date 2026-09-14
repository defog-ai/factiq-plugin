{
  "schema": "bls",
  "dataset_code": "ln",
  "title": "Labor Force Statistics from the Current Population Survey",
  "topic": "National labor force status: employment, unemployment, the unemployment rate, labor force participation and the employment-population ratio, monthly.",
  "methodology": "The Current Population Survey is a monthly sample survey of about 60,000 households conducted by the U.S. Census Bureau for the Bureau of Labor Statistics. Data describe the calendar week containing the 12th of the month.",
  "discontinuities": "At the end of each calendar year BLS re-estimates seasonal factors and revises the previous 5 years of seasonally adjusted history. Not seasonally adjusted data are final when published.",
  "latest_period_end": "2026-08-01",
  "freshness": {
    "status": "available",
    "refreshed_at": "2026-09-14T11:00:00+00:00",
    "source": "bls.series.end_time (dataset MAX)"
  },
  "last_release_date": "2026-09-04",
  "next_release_date": "2026-10-02",
  "release_cadence": "Monthly (12 releases in the last 12 months, from the source calendar)",
  "release_metadata": {
    "status": "available",
    "source": "BLS release calendar (bls.ics)",
    "source_url": "https://www.bls.gov/schedule/news_release/bls.ics",
    "release_names": [
      "Employment Situation"
    ],
    "retrieved_at": "2026-09-14T12:00:00+00:00",
    "note": "Publication dates from the BLS release calendar (bls.ics) as read at retrieved_at: last_release_date is the latest calendar date on or before that read, next_release_date the first scheduled date after it. release_cadence is observed from the calendar's past dates. Observation periods and freshness.refreshed_at are not release dates."
  },
  "frequency": "monthly",
  "dimensions": [
    {
      "dimension_type": "seasonality",
      "values": [
        "Seasonally adjusted",
        "Not seasonally adjusted"
      ]
    },
    {
      "dimension_type": "lfst",
      "values": [
        "Unemployment rate",
        "Employment level",
        "Labor force level",
        "Participation rate"
      ]
    },
    {
      "dimension_type": "ages",
      "values": [
        "16 years and over",
        "16 to 19 years",
        "25 to 54 years",
        "55 years and over"
      ]
    }
  ],
  "example_series": [
    {
      "series_id": "LNS14000000",
      "title": "Seasonally adjusted unemployment rate for people aged 16 years and over",
      "units": "Percent or rate",
      "frequency": "monthly",
      "begin_time": "1948-01-01",
      "end_time": "2026-08-01"
    },
    {
      "series_id": "LNS11300000",
      "title": "Seasonally adjusted labor force participation rate for people aged 16 years and over",
      "units": "Percent or rate",
      "frequency": "monthly",
      "begin_time": "1948-01-01",
      "end_time": "2026-08-01"
    },
    {
      "series_id": "LNS12000000",
      "title": "Seasonally adjusted employment level for people aged 16 years and over",
      "units": "Number in thousands",
      "frequency": "monthly",
      "begin_time": "1948-01-01",
      "end_time": "2026-08-01"
    }
  ]
}
