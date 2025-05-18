from abtest.scoring import TrueSkillSystem, EloSystem
from abtest.testing import TestingSystem
from abtest.utils import print_results
import numpy as np

true_skills = {
    "Goblin": 10,
    "Knight": 20,
    "Wizard": 30,
    "Rogue": 40,
    "Bard": 50,
    "Dragon": 60
}

def noisy_simulate(name1, name2, noise=5.0):
    s1 = true_skills[name1] + np.random.normal(0, noise)
    s2 = true_skills[name2] + np.random.normal(0, noise)
    return name1 if s1 > s2 else name2

for system_name, system_class in [("EloSystem", EloSystem), ("TrueSkillSystem", TrueSkillSystem)]:
    print(f"\n=== Running {system_name} ===")
    system = TestingSystem(system_class())
    results = system.run_simulation(true_skills, simulate_match=noisy_simulate, rounds=500)
    print_results(results, true_skills, title=system_name)
