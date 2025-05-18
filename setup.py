from setuptools import setup, find_packages

setup(
    name="abtest",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.22.4,<2.3.0",
        "scipy>=1.10",
        "trueskill>=0.4.5"
    ],
    author="Sage-bomb & Voxa",
    description="Skill-based A/B ranking with Elo and TrueSkill systems",
    python_requires=">=3.8",
)
