from dagster import Definitions
from my_dagster_project.jobs.pipeline_job import telegram_pipeline_job
from dagster import ScheduleDefinition

my_schedule = ScheduleDefinition(
    job=telegram_pipeline_job,
    cron_schedule="0 * * * *",  # every hour
)

defs = Definitions(
    jobs=[telegram_pipeline_job],
    schedules=[my_schedule]
)