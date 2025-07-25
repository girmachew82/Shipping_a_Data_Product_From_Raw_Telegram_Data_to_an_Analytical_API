from dagster import op
import subprocess

@op
def run_dbt_transformations(context, status: str):
    context.log.info("Running dbt transformations...")

    result = subprocess.run(["dbt", "run"], capture_output=True, text=True)
    context.log.info(result.stdout)

    if result.returncode != 0:
        context.log.error("DBT failed!")
        raise Exception("DBT run failed.")

    return "dbt_complete"
