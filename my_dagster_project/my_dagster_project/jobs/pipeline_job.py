from dagster import job
from my_dagster_project.ops.telegram_scraper import scrape_telegram_data
from my_dagster_project.ops.load_postgres import load_raw_to_postgres
from my_dagster_project.ops.run_dbt import run_dbt_transformations
from my_dagster_project.ops.yolo_detection import run_yolo_enrichment

@job
def telegram_pipeline_job():
    data = scrape_telegram_data()
    load = load_raw_to_postgres(data)
    transformed = run_dbt_transformations(load)
    run_yolo_enrichment(transformed)
