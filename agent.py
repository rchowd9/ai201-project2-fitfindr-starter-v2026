"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re
import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── query parsing ─────────────────────────────────────────────────────────────

def _parse_query(query: str) -> dict:
    """
    Extract size, max_price, and plain text description from a natural language query.
    Uses regular expressions to isolate dollar limits and size tokens.
    """
    text = query.lower()
    
    # Extract max_price (e.g. "under $30", "$30", "under 30 dollars")
    max_price = None
    price_match = re.search(r'(?:under|\$)\s*(\d+(?:\.\d+)?)', text)
    if price_match:
        max_price = float(price_match.group(1))

    # Extract common size tokens
    size = None
    size_match = re.search(r'\b(xxs|xs|s|m|l|xl|xxl|w\d+\s*l\d+|us\s*\d+(?:\.\d+)?)\b', text)
    if size_match:
        size = size_match.group(1).upper()

    # Clean description by stripping price and size phrases
    clean_desc = query
    if price_match:
        clean_desc = re.sub(r'(?:under\s*)?\$?\s*\d+(?:\.\d+)?(?:\s*dollars)?', '', clean_desc, flags=re.IGNORECASE)
    if size_match:
        clean_desc = re.sub(r'\b(?:size\s*)?' + re.escape(size_match.group(0)) + r'\b', '', clean_desc, flags=re.IGNORECASE)
    
    # Strip common query filler words
    clean_desc = re.sub(r'\b(looking for|find|search|under|size|a|an|the)\b', '', clean_desc, flags=re.IGNORECASE)
    clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()

    return {
        "description": clean_desc or query,
        "size": size,
        "max_price": max_price,
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.
    """
    session = new_session(query, wardrobe)
    iteration_count = 0

    # Iteration check 1
    iteration_count += 1
    trace.check_iterations(iteration_count)

    # Step 1: Parse the user query and store in session
    parsed = _parse_query(session["query"])
    session["parsed"] = parsed

    # Step 2: Search listings using parsed parameters
    search_results = search_listings(
        description=session["parsed"].get("description", ""),
        size=session["parsed"].get("size"),
        max_price=session["parsed"].get("max_price"),
    )
    session["search_results"] = search_results

    # ⚠️ THE BRANCH: If no listings match, stop and set helpful error message
    if not session["search_results"]:
        filters = []
        if session["parsed"].get("max_price") is not None:
            filters.append(f"price ceiling (${session['parsed']['max_price']:.2f})")
        if session["parsed"].get("size"):
            filters.append(f"size '{session['parsed']['size']}'")
        if session["parsed"].get("description"):
            filters.append(f"keywords '{session['parsed']['description']}'")

        filter_str = " or ".join(filters) if filters else "search terms"
        session["error"] = (
            f"No matching listings were found. Try adjusting your {filter_str} "
            "to broaden the search."
        )
        return session

    # Iteration check 2
    iteration_count += 1
    trace.check_iterations(iteration_count)

    # Step 3: Select the top match from search results in session
    session["selected_item"] = session["search_results"][0]

    # Step 4: Suggest an outfit using the selected item from session
    selected_item = session["selected_item"]
    user_wardrobe = session["wardrobe"]
    outfit_suggestion = suggest_outfit(new_item=selected_item, wardrobe=user_wardrobe)
    session["outfit_suggestion"] = outfit_suggestion

    # Iteration check 3
    iteration_count += 1
    trace.check_iterations(iteration_count)

    # Step 5: Create a fit card using the outfit suggestion from session
    outfit = session["outfit_suggestion"]
    fit_card = create_fit_card(outfit=outfit, new_item=session["selected_item"])
    session["fit_card"] = fit_card

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    happy_session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    _show(happy_session)
    print("\n--- Full Happy Path Session Dump ---")
    print(happy_session)

    print("\n=== A query it can't ===")
    empty_session = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    _show(empty_session)
    print("\n--- Full Empty Path Session Dump ---")
    print(empty_session)

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )