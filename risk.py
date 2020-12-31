import heuristics
import lookup


# Calculate the risk score for a given URL
def get_risk_score(url, use_vt=True):
    score = 0

    if use_vt:
        vt_results = lookup.virustotal(url)
        if vt_results["stats"]["malicious"] > 1:
            score = 100
        elif vt_results["stats"]["malicious"] == 1:
            score = 50

    heuristic_results = heuristics.run_tests(url)
    score += (sum(res.risk_value for res in heuristic_results) * 100)

    return min(100, score)

