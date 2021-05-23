"""CSC111 Project Part 2: constructing the graph
"""
from __future__ import annotations
from typing import Dict, Tuple, List, Any, Union


class _Team:
    """A vertex in a match result graph, used to represent a team

    Instance Attributes:
        - item: The team name.
        - matches: The teams that are adjacent to this team.
        - past_matches: The recent 10 matches opponents and the score

    Representation Invariants:
        - self not in self.matches
        - all(self in u.matches for u in self.matches)
    """
    item: Any
    matches: Dict[_Team, Union[int, float]]
    past_matches: List[Tuple[_Team, Union[int, float]]]

    def __init__(self, item: Any) -> None:
        """Initialize a new vertex with the given item.

        This vertex is initialized with no matches.
        """
        self.item = item
        self.matches = {}
        self.past_matches = []

    def recent_performance(self) -> float:
        """Return the average score of self.past_matches"""
        recent_matches = 0
        recent_score = 0
        for match in self.past_matches:
            recent_score += match[1]
            recent_matches += 1

        if recent_matches != 0:
            return recent_score / recent_matches
        else:
            return -50


class MatchGraph:
    """A weighted graph used to represent a book review network that keeps track of review scores.
    """
    # Private Instance Attributes:
    #     - _teams:
    #           A collection of the teams contained in this graph.
    #           Maps item to _Team object.
    #     - _all_matches:
    #           A collection of the edges contained in this graph.
    #           Maps (Home, Away) to weight
    #     - _seasonal_weight:
    #           A float that decides the weight of current score.
    #           i.e. when the season changes, the weight of all current
    #           edges are going to *_seasonal_weight.
    _teams: Dict[str, _Team]
    _all_matches: Dict[Tuple, Union[int, float]]
    _seasonal_weight: Union[int, float]

    def __init__(self, weight) -> None:
        """Initialize an empty graph (no vertices or edges) with given seasonal_weight.
        """
        self._all_matches = {}
        self._teams = {}
        self._seasonal_weight = weight

    def add_data(self, row: list) -> None:
        """Add the given row of data into the graph.
        row[0] is season
        row[1] home
        row[2] away
        row[3] score
        """
        # add the two teams if they don't exist in the current dict
        if not self.include_team(row[1]):
            self.add_team(row[1])
        if not self.include_team(row[2]):
            self.add_team(row[2])

        if not self.include_edge(row[1], row[2]):
            self.add_edge(row[1], row[2], row[3])
        else:
            self.update_edge(row[1], row[2], row[3])

        self.update_recent_match(row[1], row[2], row[3])

    def include_team(self, team: str) -> bool:
        """Check if the given item is in the graph, specifically in self._teams
        """
        return team in self._teams

    def add_team(self, team: str) -> None:
        """Add the given team into self._teams.
        """
        temp = _Team(team)
        self._teams[team] = temp

    def include_edge(self, home: str, away: str) -> bool:
        """Check if the two teams have played against each other.

        Preconditions:
         - 'home' in home
         - 'away' in away

        this means that there should not be any home team with away
        labels. Vice versa.
        """
        temp = (home, away)
        return temp in self._all_matches

    def add_edge(self, home: str, away: str, score: Union[int, float]) -> None:
        """Add the given edge into self._all_matches.

        Preconditions:
         - 'home' in home
         - 'away' in away
         - home in self._teams
         - away in self._teams
        """
        temp = (home, away)
        home_team = self._teams[home]
        away_team = self._teams[away]

        # add the teams to each other's match record
        home_team.matches[away_team] = score
        away_team.matches[home_team] = score

        # add the two teams into self._all_matches
        self._all_matches[temp] = score

    def get_edge(self, home: str, away: str) -> float:
        """Get the value of the edge between the given teams.

        Preconditions:
         - 'home' in home
         - 'away' in away
         - home in self._teams
         - away in self._teams

        return -50 if there is no edge between the given team.
        """
        temp = (home, away)
        if temp in self._all_matches:
            return self._all_matches[temp]
        else:
            return -50

    def update_edge(self, home: str, away: str, score: Union[int, float]) -> None:
        """update the given edge with new score.

        Preconditions:
         - 'home' in home
         - 'away' in away
         - home in self._teams
         - away in self._teams
        """
        # calculate the new score
        temp_tuple = (home, away)
        curr_score = self._all_matches[temp_tuple] + score

        # add the new score in teams
        home_team = self._teams[home]
        away_team = self._teams[away]
        home_team.matches[away_team] = curr_score
        away_team.matches[home_team] = curr_score

        # add the new score to self._all_matches
        self._all_matches[temp_tuple] = curr_score

    def update_recent_match(self, home: str, away: str, score: int) -> None:
        """Update each other into _Team.past_matches.
        if the list has more than 10 items, remove the last one.

        Preconditions:
         - 'home' in home
         - 'away' in away
         - home in self._teams
         - away in self._teams
        """
        home_team = self._teams[home]
        away_team = self._teams[away]

        if len(home_team.past_matches) >= 10:
            home_team.past_matches.pop(0)
        if len(away_team.past_matches) >= 10:
            away_team.past_matches.pop(0)

        home_team.past_matches.append((away_team, score))
        away_team.past_matches.append((home_team, score))

    def get_performance(self, team) -> float:
        """Get the performance of the given team

        """
        if team in self._teams:
            temp = self._teams[team]
            return temp.recent_performance()
        else:
            return -50

    def update_season(self) -> None:
        """update the graph into a new season.
        i.e. all the weight of the edges should be changed with factor _seasonal_weight.
        """
        for key in self._all_matches:
            self._all_matches[key] = self._all_matches[key] \
                                     * self._seasonal_weight

        for team in self._teams:
            curr_team = self._teams[team]
            for key in curr_team.matches:
                curr_score = curr_team.matches[key]
                curr_score = curr_score * self._seasonal_weight
                curr_team.matches[key] = curr_score
