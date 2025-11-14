# SG Tax Pipeline

---

## Running with `uv`

From project root:

### 1. Install dependencies

```bash
uv sync
```

### 2. Run the pipeline

With defaults:

```bash
uv run taxpipeline
```

With explicit arguments (positional):

```bash
taxpipeline individual_tax_returns.csv artifacts configs/config.yaml
```

Defaults if omitted:

- `input_path` → `individual_tax_returns.csv`
- `outdir` → `artifacts`
- `config_path` → `configs/config.yaml`

---

## Config & Logging

- Application config: `configs/config.yaml`
  - Loaded via Pydantic Settings
  - Values can be overridden by environment variables using `__` nesting (e.g. `PATHS__CURATED_DIR=/data/curated`)

- Logging config path is defined in `config.yaml` under:

  ```yaml
  paths:
    logging_config: "configs/logging.yaml"
  ```

- Logging YAML: `configs/logging.yaml`
  - Console + rotating file handlers
  - Can be swapped per-environment by changing `paths.logging_config` or overriding via env var.

---

## Dimensional Model (Star Schema)

Curated outputs follow a star schema:

- `dim_taxpayer`
- `dim_time`
- `dim_location`
- `dim_occupation`
- `fact_tax_returns`

---

## Outputs

When the pipeline runs, it produces:

- Parquet dim/fact tables in: `artifacts/curated/`
  - `dim_taxpayer.parquet`
  - `dim_time.parquet`
  - `dim_location.parquet`
  - `dim_occupation.parquet`
  - `fact_tax_returns.parquet`

- Data quality artefacts:
  - Row-level report: `artifacts/dq_report.csv`
  - Summary stats: `artifacts/dq_summary.json`

---

## Docker

You can also run the pipeline containerised.

From the `docker/` directory:

```bash
docker compose build
docker compose up
```

This will:

- Build an image from `docker/Dockerfile`
- Run the pipeline in a container using:
  - `../individual_tax_returns.csv` mounted at `/app/individual_tax_returns.csv`
  - `../artifacts` mounted at `/app/artifacts`
  - `../configs` mounted at `/app/configs`

- Use the entrypoint: `tax-pipeline /app/individual_tax_returns.csv /app/artifacts configs/config.yaml`

---

## Tests

Run unit tests (validators, etc.) using `uv`:

```bash
uv sync
uv run pytest
```

---

## High-level Flow

1. **Ingestion**: Read `individual_tax_returns.csv`
2. **Standardisation**: Type coercion, basic cleaning (`transforms.standardize`)
3. **Data Quality**:
   - Apply rule-based validators (`validators.py`)
   - Compute per-row DQ score (`dq.py`)
   - Persist DQ report + summary

4. **Dimensional Modelling**:
   - Build dims + fact (`transforms.build_dims_and_fact`)
   - Write Parquet tables to curated zone

5. **Consumption**:
   - Downstream tools (Athena, Spark, BI) can query curated tables and use DQ metrics for governance.

```

```
