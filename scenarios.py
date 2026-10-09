"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # Criterion 3 — state. Any normal query works; what's being checked is
        # that the id in session["selected_item"] is the id that reaches
        # suggest_outfit, which the trace prints on the suggest_outfit step.
        "name": "selected item survives into suggest_outfit",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4 — the fit card. The same query five times, because the
        # criterion is about what stays constant across runs that differ in
        # wording: title, price and platform.
        "name": "fit card keeps the key facts across runs",
        "query": "90s leather bomber jacket",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5 — the price ceiling. A tight ceiling, so a listing that
        # slipped past the filter would be visible in the results.
        "name": "price ceiling holds",
        "query": "vintage tee under $20",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Diagnostic. The data holds lst_001, "Vintage Levi's 501 Jeans", so
        # this query is matchable. If the agent stops early here, the stop is
        # a false empty and the cause is upstream of the branch.
        "name": "possessive in the query (false empty)",
        "query": "looking for levi's 501s",
        "wardrobe": "example",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
