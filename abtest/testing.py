"""TestingSystem class with EIG-based pairing."""

from scipy.stats import kendalltau
import numpy as np
from .core import Element
import json


class TestingSystem:
    def __init__(self, scoring_system):
        self.scoring_system = scoring_system
        self.elements = {}

    def add_element(self, name):
        element = Element(name, self.scoring_system.create_rating())
        self.elements[name] = element

    def record_match(self, winner_name, loser_name):
        winner = self.elements[winner_name]
        loser = self.elements[loser_name]
        winner.rating, loser.rating = self.scoring_system.update_ratings(winner.rating, loser.rating)
        winner.record_match(loser.id, 'win')
        loser.record_match(winner.id, 'loss')

    def get_rankings(self):
        return sorted(self.elements.values(), key=lambda e: self.scoring_system.extract_mu(e.rating), reverse=True)

    def suggest_pair(self):
        names = list(self.elements.keys())
        candidates = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a = self.elements[names[i]]
                b = self.elements[names[j]]

                mu_a = self.scoring_system.extract_mu(a.rating)
                mu_b = self.scoring_system.extract_mu(b.rating)
                sigma_a = self.scoring_system.extract_sigma(a.rating)
                sigma_b = self.scoring_system.extract_sigma(b.rating)

                mu_diff = abs(mu_a - mu_b)
                sigma_sum = sigma_a + sigma_b
                info_gain = (sigma_sum + 1e-5) / (mu_diff + 1e-5)
                candidates.append((info_gain, (a.name, b.name)))

        candidates.sort(reverse=True)
        return candidates[0][1] if candidates else (None, None)

    def run_simulation(self, true_skills, simulate_match, rounds=100):
        names = list(true_skills.keys())
        for name in names:
            self.add_element(name)

        prev_ranking = None
        for round in range(rounds):
            a, b = self.suggest_pair()
            if a is None or b is None:
                break

            winner = simulate_match(a, b)
            loser = b if winner == a else a
            self.record_match(winner, loser)

            if round % 10 == 0:
                if self.has_converged(prev_ranking=prev_ranking):
                    print(f"✅ Converged at round {round}")
                    break
                prev_ranking = [e.name for e in self.get_rankings()]

        return self.get_rankings()


    def has_converged(self, threshold_sigma=2.0, prev_ranking=None, tau_threshold=0.98):
        # Only TrueSkill uses sigma decay
        if hasattr(self.scoring_system, "extract_sigma") and not isinstance(self.scoring_system, EloSystem):
            max_sigma = max(self.scoring_system.extract_sigma(e.rating) for e in self.elements.values())
            if max_sigma > threshold_sigma:
                return False

        # Tau convergence check for all systems
        if prev_ranking:
            current = [e.name for e in self.get_rankings()]
            tau, _ = kendalltau(prev_ranking, current)
            return tau >= tau_threshold

        return False
    


    def save_state(self, filepath):
        data = {
            "elements": {
                name: {
                    "id": e.id,
                    "mu": self.scoring_system.extract_mu(e.rating),
                    "sigma": getattr(e.rating, "sigma", 0),
                    "history": e.history
                } for name, e in self.elements.items()
            }
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_state(self, filepath):
        import importlib

        try:
            trueskill_mod = importlib.import_module("trueskill")
            TS_Rating = trueskill_mod.Rating
        except ImportError:
            TS_Rating = None

        with open(filepath, "r") as f:
            data = json.load(f)

        for name, info in data["elements"].items():
            rating = self.scoring_system.create_rating()

            if TS_Rating and isinstance(rating, TS_Rating):
                rating = TS_Rating(mu=info["mu"], sigma=info["sigma"])
            elif hasattr(rating, "mu"):
                rating.mu = info["mu"]
                try:
                    rating.sigma = info["sigma"]
                except AttributeError:
                    pass  # Read-only, e.g., Elo
            elif hasattr(rating, "elo"):
                rating.elo = info["mu"]

            e = Element(name, rating)
            e.id = info["id"]
            e.history = info["history"]
            self.elements[name] = e