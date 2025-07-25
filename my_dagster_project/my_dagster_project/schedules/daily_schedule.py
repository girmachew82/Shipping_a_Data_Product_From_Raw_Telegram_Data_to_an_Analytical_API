from dagster import schedule
from my_dagster_project.jobs.pipeline_job import telegram_pipeline_job

@schedule(cron_schedule="0 6 * * *", job=telegram_pipeline_job, execution_timezone="UTC")
def daily_schedule():
    return {}
