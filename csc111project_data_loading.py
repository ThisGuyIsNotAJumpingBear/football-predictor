"""CSC111 Project Part 1: Reading the data
"""
import csv
from typing import List


def read_file(path: str) -> List[list]:
    """
    Read the data from the file path, reconstruct the format the the data
    and return a list of lines.

    the shape of the output is:
    [[season, home_team, away_team, full_time_performance_score],
    ...]

        Preconditions:
         - the file input follows the same format with Lalia_full_data.csv
    """
    lst = []
    season_count = -1
    prev_season = 'n/a'
    with open(path) as league_data:
        reader = csv.reader(league_data)
        next(reader)  # skip the header row)

        for row in reader:
            # retrieve the data
            curr_season, home, away = row[0], row[2], row[3]
            home_goal, away_goal = int(row[4]), int(row[5])

            # edit the data
            if curr_season != prev_season:
                season_count += 1
                prev_season = curr_season
            home = home + ' home'  # add a label to the home team
            away = away + ' away'  # add a label to the away team

            perf = home_goal - away_goal

            # store the data
            temp = [season_count, home, away, perf]
            lst.append(temp)
    return lst


if __name__ == '__main__':
    import pprint
    file_path = 'Laliga_data_small.csv'
    test_data = read_file(file_path)
    pprint.pprint(test_data)
