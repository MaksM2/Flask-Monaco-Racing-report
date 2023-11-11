

import re

from datetime import datetime

from app.bl.report.provider import read_log_files
from app.db.models.result import Result
from app.db.models.driver import Driver, Team
from app.db.models.race import Race
from app.db.models.stage import Stage

from app.db.session import s
from app.config import FOLDER_DATA


PATTERN = re.compile(r'(^[A-Z]+)(\S+)')
DATE_FORMAT = '%Y-%m-%d_%H:%M:%S.%f'

RACE = Race(name='Monaco Racing', year=2018)
STAGE = Stage(name='Q3')


def convert_and_store_data(folder_path: str = FOLDER_DATA) -> None:
    """This function convert data from log files and stores it to database

    :param folder_path: path to the folder with log files
    """
    start_log, end_log, abbreviations_data = read_log_files(folder_path)

    prepare_start = _prepare_data_from_file(start_log)
    prepare_end = _prepare_data_from_file(end_log)

    teams = set()
    driver_results = []

    for param in abbreviations_data:
        abbr, name, team_name = param.strip().split('_')
        start, end = prepare_start[abbr], prepare_end[abbr]

        team = next((team for team in teams if team.name == team_name), None)
        if team is None:
            team = Team(name=team_name)
            teams.add(team)

        driver = Driver(abbr=abbr, name=name, team=team)
        result = Result(
            driver=driver, race=RACE, stage=STAGE, start=start, end=end
        )
        driver_results.append(result)

    s.user_db.add_all(sort_results(driver_results))


def _prepare_data_from_file(file_data: list[str]) -> dict[str, datetime]:
    """This function takes data from log file and prepare it

    :param file_data: file where we take data
    :return: dictionary, where abbreviation is key, start lap time - is value
    """

    prepare_result = {}

    for param in file_data:
        match = PATTERN.match(param)
        assert match
        abbr, time = match.groups()
        prepare_result[abbr] = datetime.strptime(time, DATE_FORMAT)

    return prepare_result


def sort_results(driver_results: list[Result]) -> list[Result]:
    """This function sorts results by his owner inside a database for and set
    position to each

    :return: List of sorted Result with position
    """
    sorted_result = sorted(
        driver_results,
        key=lambda item: (item.total_seconds < 0, abs(item.total_seconds))
    )

    for pos, result in enumerate(sorted_result, start=1):
        result.position = pos

    return sorted_result
