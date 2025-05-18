import os
import sys
import tempfile
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scipy.stats import kendalltau
from abtest.scoring import EloSystem
from abtest.testing import TestingSystem
from abtest.utils import print_results

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

# Load available systems
systems = {
    "EloSystem": EloSystem(),
}

print("🔍 Checking for TrueSkillSystem support...")
try:
    from abtest.scoring import TrueSkillSystem
    _ = TrueSkillSystem()
    systems["TrueSkillSystem"] = TrueSkillSystem()
    print("✅ TrueSkillSystem is available and will be tested.")
except (ImportError, AttributeError) as e:
    print("⚠️  TrueSkillSystem not available. Skipping.")

# Execute validation loop
for name, system in systems.items():
    print(f"\n=== Running {name} ===")
    test = TestingSystem(system)

    results1 = test.run_simulation(true_skills, simulate_match=noisy_simulate, rounds=300)
    print_results(results1, true_skills, title=f"{name} Phase 1")

    tmp_path = os.path.join(tempfile.gettempdir(), f"{name}_state.json")
    test.save_state(tmp_path)

    test2 = TestingSystem(system.__class__())
    test2.load_state(tmp_path)
    results2 = test2.run_simulation(true_skills, simulate_match=noisy_simulate, rounds=300)
    print_results(results2, true_skills, title=f"{name} Phase 2")

    tau, _ = kendalltau(
        [e.name for e in results1],
        [e.name for e in results2]
    )
    print(f"🔎 Kendall Tau after reload: {tau:.2f}")
    assert tau > 0.9, f"{name} ranking diverged post-load"

print("\n✅ All systems passed validation.")
