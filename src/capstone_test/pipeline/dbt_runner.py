import subprocess

from capstone_test.core.logging import logger

_DBT_COMMANDS = {
    "staging": ["dbt", "run", "--select", "staging"],
    "marts": ["dbt", "run", "--select", "marts"],
    "test": ["dbt", "test"],
}

_DBT_PROJECT_DIR = "HOUSING_ANALYTICS"


def run(step: str) -> None:
    if step not in _DBT_COMMANDS:
        raise ValueError(f"Unknown dbt step '{step}'. Valid steps: {list(_DBT_COMMANDS)}")

    command = _DBT_COMMANDS[step]
    logger.info(f"dbt: running step '{step}' → {' '.join(command)}")

    result = subprocess.run(
        command,
        cwd=_DBT_PROJECT_DIR,
        capture_output=True,
        text=True,
    )

    for output_line in result.stdout.splitlines():
        logger.info(f"dbt | {output_line}")
    for error_line in result.stderr.splitlines():
        logger.warning(f"dbt | {error_line}")

    if result.returncode != 0:
        raise RuntimeError(f"dbt step '{step}' failed with exit code {result.returncode}")

    logger.info(f"dbt: step '{step}' completed successfully")