"""Core classes and testing logic for the AB testing suite."""

import uuid

class Element:
    def __init__(self, name, rating):
        self.name = name
        self.id = str(uuid.uuid4())
        self.rating = rating
        self.history = []

    def record_match(self, opponent_id, result):
        self.history.append({"opponent_id": opponent_id, "result": result})

    def conservative_score(self):
        if hasattr(self.rating, "sigma"):
            return self.rating.mu - 3 * self.rating.sigma
        return self.rating.mu

    def match_count(self):
        return len(self.history)
