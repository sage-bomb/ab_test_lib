"""Scoring systems: TrueSkill and ELO support."""

try:
    from trueskill import Rating, rate_1vs1
    TRUESKILL_AVAILABLE = True
except ImportError:
    TRUESKILL_AVAILABLE = False
    Rating = None
    rate_1vs1 = None

class ScoringSystem:
    def create_rating(self):
        raise NotImplementedError

    def update_ratings(self, winner_rating, loser_rating):
        raise NotImplementedError

    def extract_mu(self, rating):
        raise NotImplementedError

    def extract_sigma(self, rating):
        raise NotImplementedError

if TRUESKILL_AVAILABLE:
    class TrueSkillSystem(ScoringSystem):
        def create_rating(self):
            return Rating()

        def update_ratings(self, winner_rating, loser_rating):
            return rate_1vs1(winner_rating, loser_rating)

        def extract_mu(self, rating):
            return rating.mu

        def extract_sigma(self, rating):
            return rating.sigma


class EloRating:
    def __init__(self, rating=1500):
        self._rating = rating

    @property
    def mu(self):
        return self._rating

    @mu.setter
    def mu(self, value):
        self._rating = value

    @property
    def sigma(self):
        return 200  # Fixed uncertainty placeholder

    @property
    def elo(self):
        return self._rating

    @elo.setter
    def elo(self, value):
        self._rating = value

    def __repr__(self):
        return f"ELO={self._rating:.1f}"


class EloSystem(ScoringSystem):
    def __init__(self, k=32):
        self.k = k

    def create_rating(self):
        return EloRating()

    def update_ratings(self, winner_rating, loser_rating):
        expected_winner = 1 / (1 + 10 ** ((loser_rating.mu - winner_rating.mu) / 400))
        expected_loser = 1 - expected_winner

        winner_rating.mu += self.k * (1 - expected_winner)
        loser_rating.mu += self.k * (0 - expected_loser)
        return winner_rating, loser_rating

    def extract_mu(self, rating):
        return rating.mu

    def extract_sigma(self, rating):
        return rating.sigma
