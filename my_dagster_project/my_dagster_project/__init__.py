from dagster import Definitions
from jobs.pipeline_job import telegram_pipeline_job

defs = Definitions(jobs=[telegram_pipeline_job])
