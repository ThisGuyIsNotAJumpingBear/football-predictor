"""CSC111 Project Part 3: constructing the predictor object
"""
from csc111project_graph import MatchGraph
import random
import numpy as np


class Predictor:
    """A graph-based entity that predicts scores for matches.

    Instance Attributes:
     - graph: The book review graph that this entity uses to make predictions.
     - curr_season: the number of seasons from the first one in the data.
        i.e. in Laliga_full_data.csv, the first season is 1995-96 so if the current
        data is in 1998-99, curr_season will be 3.
     - seasonal_weight: a float decides the weight of each season.
     - accuracy: a list prediction accuracies for all the past seasons.
     - curr_sum_score: the accuracy of the current season.
     - curr_matches: the number of matches played in the current season.
    """
    graph: MatchGraph
    curr_season: int
    seasonal_weight: float
    accuracy: list
    curr_sum_score: float
    curr_matches: int

    def __init__(self, weight: float) -> None:
        """Initialize a new predictor."""
        self.graph = MatchGraph(weight)
        self.seasonal_weight = weight
        self.curr_season = 0
        self.curr_sum_score = 0
        self.curr_matches = 0
        self.accuracy = []

    def predict(self, home: str, away: str) -> int:
        """Return the predicted score between the home and the away team.

        This method will find the edge between the two teams.

        If the edge is found, the predictor will return the weight of the edge;

        If the edge is not found, the predictor will find the teams' recent performance
        scores. A rounded value of the difference between their recent performance
        will be returned.

        If the two teams do not have recent performance data, the predictor will make
        a random choice in [-1, 1].
        """
        prediction = self.graph.get_edge(home, away)
        # print(prediction)
        # graph.get_edge will return -50 if there are no edges between the given teams

        if prediction != -50:
            return self.round_score(prediction)
        else:
            # if there are no edges between them
            home_recent = self.graph.get_performance(home)
            away_recent = self.graph.get_performance(away)
            if home_recent != -50 and away_recent != -50:
                performance_diff = home_recent - away_recent
                return self.round_score(performance_diff)
            else:
                return random.randint(-1, 1)

    def feed_data(self, row: list) -> None:
        """feed a row of data into the predictor.

        The predictor should make a prediction first. Then, the prediction is compared with
        the actual result to find the accuracy.
        """
        season = row[0]
        home = row[1]
        away = row[2]
        actual_score = row[3]

        # if the object need to change the current season
        if season != self.curr_season:
            self.graph.update_season()
            self.curr_season = season
            self.accuracy.append(self.get_accuracy())
            self.curr_matches = 0
            self.curr_sum_score = 0

        pred_score = self.predict(home, away)
        self.graph.add_data(row)
        self.update_curr_accuracy(pred_score, actual_score)

    def update_curr_accuracy(self, pred: int, actu: int) -> None:
        """update the accuracy score of the predictor.

        Separate the 7 possible scores: -3, -2, -1, 0, 1, 2, 3
        we consider:
        group 1: -3, -2: the home has high possibility to lose
        group 2: -1, 0, 1: the two teams are similar so it depends
        group 3: 2, 3: the home has high possibility to win

        if the prediction matches exactly with the actual score, we give it 1.
        However, if it does not, we do not simply give it a 0, but see how close it is
        with the actual score.

        if the two scores falls in group 1 and 3, we give it a 0.75 because it correctly
        predicts the result of the match. The only difference is about the goals.

        if the two scores falls in group 2, we give it a 0.5 if the difference in prediction is 1
        because although it makes some mistakes but that is due to that the two team under
        evaluation is so close to each other.
        """
        self.curr_matches += 1
        if pred == actu:
            self.curr_sum_score += 1
            return
        elif pred <= -2 and actu <= -2:
            self.curr_sum_score += 0.75
            return
        elif pred >= 2 and actu >= 2:
            self.curr_sum_score += 0.75
            return
        elif pred in {-1, 0, 1} and actu in {-1, 0, 1}:
            if abs(pred - actu) == 1:
                self.curr_sum_score += 0.5
                return

    # def convert_weighted_score(self, score: float) -> int:
    #     """convert the weighted score into a unweighted version."""
    #     # represents the score if the  two teams have a
    #     # performance difference score 3, 2, 1 in all the seasons.
    #     # see csc111project_data_loading.py for actual calculation of
    #     # the performance difference.
    #     boundary_3 = 0
    #     boundary_2 = 0
    #     boundary_1 = 0
    #
    #     for i in range(1, self.curr_season + 1):
    #         boundary_3 += 3 * (self.seasonal_weight ** i)
    #         boundary_2 += 2 * (self.seasonal_weight ** i)
    #         boundary_1 += 1 * (self.seasonal_weight ** i)
    #
    #     # a list store the distance of score to each boundary.
    #     # index(min(dist)) - 3 is the no. of the boudnary.
    #     dist = [score + boundary_3, score + boundary_2, score + boundary_1,
    #             score, score - boundary_1, score - boundary_2, score - boundary_3]
    #     return dist.index(min(dist))

    def round_score(self, score: float) -> int:
        """round the score."""
        if score >= 3:
            return 3
        elif 1.5 <= score < 3:
            return 2
        elif 0.05 <= score < 1.5:
            return 1
        elif -0.05 < score < 0.05:
            return 0
        elif -1.5 < score <= -0.05:
            return -1
        elif -3 < score <= -1.5:
            return -2
        else:
            return -3

    def get_accuracy(self) -> float:
        """get the accuracy of the predictor currently in this season."""
        return self.curr_sum_score / self.curr_matches

    def get_seasonal_accuracy(self) -> list:
        """get all the accuracy scores so far in a list.
        it also include the current accuracy score.
        """
        lst = self.accuracy
        lst.append(self.get_accuracy())
        return lst


class activePredictor(Predictor):
    """A predictor inherits the previous Predictor object.

    It is almost the same as the Predictor except that the boundary it uses to convert the
    weight of the edge is dynamic rather than fixed.

    Instance Attributes:
     - boundary0, 1, 2, 3: the boundary for score 0, 1, 2, 3.
     -b(0/1/2/3)_all_value: lists which store all the edge value when actual score = 0/1/2/3.

    """
    # boundary0: float
    boundary1: float
    boundary2: float
    boundary3: float
    # b0_all_value: list
    b1_all_value: list
    b2_all_value: list
    b3_all_value: list

    def __init__(self, weight: float) -> None:
        """initialize a new activePredictor object."""
        super().__init__(weight)
        self.boundary0 = 0
        self.boundary1 = 1
        self.boundary2 = 2
        self.boundary3 = 3
        self.b0_all_value = []
        self.b1_all_value = []
        self.b2_all_value = []
        self.b3_all_value = []

    def feed_data(self, row: list) -> None:
        """feed a row of data into the predictor.

        The predictor should make a prediction first. Then, the prediction is compared with
        the actual result to find the accuracy.

        The difference between prediction and actual result changes the boundary.
        """
        season = row[0]
        home = row[1]
        away = row[2]
        actual_score = row[3]

        # if the object need to change the current season
        if season != self.curr_season:
            self.graph.update_season()
            self.curr_season = season
            self.accuracy.append(self.get_accuracy())
            self.curr_matches = 0
            self.curr_sum_score = 0

        # retrieve the edge value before the data is fed.
        edge_value = self.graph.get_edge(home, away)

        pred_score = self.predict(home, away)
        self.graph.add_data(row)
        self.update_curr_accuracy(pred_score, actual_score)

        # update the boundary by the early edge and late actual score
        self.update_boundary(edge_value, actual_score)

    def round_score(self, score: float) -> int:
        """round the score."""
        abs_score = abs(score)
        # the abs value of the distance of the score to the boundaries
        dist_0 = abs(score - self.boundary0)
        dist_1 = abs(abs_score - self.boundary1)
        dist_2 = abs(abs_score - self.boundary2)
        dist_3 = abs(abs_score - self.boundary3)
        all_dist = (dist_0, dist_1, dist_2, dist_3)

        # find the closest boundary to the score
        if dist_0 == min(all_dist):
            abs_result = 0
        elif dist_1 == min(all_dist):
            abs_result = 1
        elif dist_2 == min(all_dist):
            abs_result = 2
        else:
            abs_result = 3

        if score >= 0:
            return abs_result
        else:
            return 0 - abs_result

    def update_boundary(self, edge: float, actu: int) -> None:
        """update the value of boundary by the difference between the pred and actu.

        0.05 is a constant controlled by the developer which decides how far the boundary should
        move in one prediction.

        This method will not change anything if the signs of two inputs are different.
        Everything is possible in football. We accept some abnormal matches.
        """
        a_edge = abs(edge)
        a_actu = abs(actu)
        if a_edge != 50:
            if a_actu == 0:
                self.b0_all_value.append(edge)
                # here it is edge but not a_edge because boundary0 needs to consider both
                # positive and negative cases
            if a_actu == 1:
                self.b1_all_value.append(a_edge)
            elif a_actu == 2:
                self.b2_all_value.append(a_edge)
            elif a_actu == 3:
                self.b3_all_value.append(a_edge)

        self.boundary0 = self.avg_100(self.b0_all_value)
        self.boundary1 = self.avg_100(self.b1_all_value)
        self.boundary2 = self.avg_100(self.b2_all_value)
        self.boundary3 = self.avg_100(self.b3_all_value)

    def avg_100(self, init_lst: list) -> float:
        """return the average of the last 100 elements of the list.

        Preconditions:
         - all the value in lst are ints.
        """
        lst = init_lst[-100:]

        if len(lst) != 0:
            return sum(lst) / len(lst)
        else:
            return 0


class randomPredictor(Predictor):
    """a predictor class that only gives random results"""
    def predict(self, home: str, away: str) -> int:
        """return the prediction of this predictor.

        It uses the random library to get a random int between -3 and 3 inclusive.
        """
        return random.randint(-3, 3)


class normalPredictor(Predictor):
    """a predictor class that uses a normal distribution model to give prediction.
    """
    def predict(self, home: str, away: str) -> int:
        """return the prediction of this predictor.

        it uses the normal distribution function in numpy to construct a list of values.
        then, it makes a random choice from it.
        """
        normal = np.random.normal(0, 3, 500)
        shaped_normal = [x for x in normal if -3 <= x <= 3]
        return round(random.choice(shaped_normal))
