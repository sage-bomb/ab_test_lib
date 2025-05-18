from scipy.stats import kendalltau

def print_results(results, true_skills, title=""):
    predicted = [e.name for e in results]
    true_order = sorted(true_skills.items(), key=lambda x: x[1], reverse=True)
    true_names = [name for name, _ in true_order]
    
    tau, _ = kendalltau(
        [true_names.index(name) for name in predicted],
        list(range(len(predicted)))
    )

    if title:
        print(f"🏁 {title}")
    print(f"   Matches: {sum(len(e.history) for e in results)}, Kendall Tau vs Ground Truth: {tau:.2f}")
    for e in results:
        mu = getattr(e.rating, "mu", e.rating)
        sigma = getattr(e.rating, "sigma", 0)
        conservative = mu - 3 * sigma if sigma else mu
        print(f"   {e.name:>8} | μ={mu:.2f} | σ={sigma:.2f} | Conservative={conservative:.2f} | Matches={len(e.history)}")
    print("")
