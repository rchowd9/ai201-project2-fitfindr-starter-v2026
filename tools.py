"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    wanted_sizes = _size_tokens(size) if size else set()
    query_words = _keywords(description or "")

    scored = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if wanted_sizes and not (wanted_sizes & _size_tokens(listing["size"])):
            continue

        score = _match_score(query_words, listing)
        if score > 0:
            scored.append((score, listing))

    # sort() is stable, so ties keep the dataset's order.
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# Words that say nothing about the item. Without this, "a tee for the summer"
# scores every listing whose description happens to contain "for" or "the".
_STOPWORDS = {
    "a", "an", "and", "any", "find", "for", "i", "in", "is", "it", "like",
    "looking", "me", "my", "need", "of", "on", "or", "size", "some",
    "something", "the", "to", "under", "want", "with",
}

# Where a keyword was found, and how much that counts. A word in the title or
# the tags says more about what the item *is* than a word in the description.
_FIELD_WEIGHTS = {
    "title": 3,
    "style_tags": 2,
    "category": 2,
    "colors": 2,
    "brand": 1,
    "description": 1,
}


def _normalize_word(word: str) -> str:
    """Drop a plural 's', so 'tees' matches 'tee' and 'jeans' matches 'jean'."""
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {_normalize_word(w) for w in words if w not in _STOPWORDS and len(w) > 1}


def _match_score(query_words: set[str], listing: dict) -> int:
    """Weighted count of query words that appear in each field of the listing."""
    score = 0
    for field, weight in _FIELD_WEIGHTS.items():
        value = listing.get(field)
        if not value:  # brand is None for most listings
            continue
        text = " ".join(value) if isinstance(value, list) else str(value)
        score += weight * len(query_words & _keywords(text))
    return score


def _size_tokens(size: str) -> set[str]:
    """
    Break a size string into the sizes it actually covers.

        "S/M"                  -> {"S", "M"}
        "XL (fits oversized)"  -> {"XL"}
        "US 8.5"               -> {"US8.5"}
        "W30 L30"              -> {"W30", "L30"}
        "One Size / Oversized" -> {"ONESIZE"}

    Two sizes match when they share a whole token. That's why "S" doesn't match
    "US 9" and "L" doesn't match "XL", which a substring test gets wrong.
    """
    text = size.upper()
    text = re.sub(r"ONE\s*SIZE", "ONESIZE", text)
    text = re.sub(r"\b(US|W)\s+(?=\d)", r"\1", text)
    tokens = re.findall(r"[A-Z0-9.]+", text)
    return {
        t for t in tokens
        if t in {"XXS", "XS", "S", "M", "L", "XL", "XXL", "ONESIZE"}
        or re.fullmatch(r"(US|W|L)\d+(\.\d+)?", t)
    }


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = (wardrobe or {}).get("items") or []
    item_text = _describe_item(new_item)

    if not items:
        prompt = (
            f"Someone is thinking about buying this thrifted piece:\n{item_text}\n\n"
            "We don't know what's in their wardrobe. Suggest one or two outfits "
            "built around this piece using common staples most people could find "
            "(e.g. 'straight-leg jeans', 'white sneakers'). Say what vibe each "
            "outfit gives. Keep it under 150 words."
        )
    else:
        closet = "\n".join(_describe_wardrobe_item(w) for w in items)
        prompt = (
            f"Someone is thinking about buying this thrifted piece:\n{item_text}\n\n"
            f"Here is what they already own:\n{closet}\n\n"
            "Suggest one or two complete outfits that pair the new piece with "
            "items they already own. Name the owned pieces exactly as listed. "
            "Say in one sentence why each outfit works. Keep it under 150 words."
        )

    response = generate(prompt, system=_STYLIST_SYSTEM)
    if response.strip():
        return response
    # The model occasionally sends back nothing, and the loop needs a non-empty string.
    return (
        f"Couldn't get a styling suggestion for the {new_item.get('title', 'item')} "
        "right now. Try pairing it with simple basics in a neutral color."
    )


_STYLIST_SYSTEM = (
    "You are a friendly personal stylist who specializes in thrifted and "
    "secondhand fashion. Give concrete, wearable outfit ideas. Plain text, no "
    "markdown headings."
)


def _describe_item(item: dict) -> str:
    """One listing as prompt text. Leaves brand out when there isn't one."""
    lines = [
        f"- {item.get('title', 'Untitled item')}",
        f"  Category: {item.get('category', 'unknown')}",
        f"  Colors: {', '.join(item.get('colors') or []) or 'unspecified'}",
        f"  Style: {', '.join(item.get('style_tags') or []) or 'unspecified'}",
        f"  Size: {item.get('size', 'unspecified')}, condition: {item.get('condition', 'unspecified')}",
    ]
    if item.get("brand"):
        lines.append(f"  Brand: {item['brand']}")
    if item.get("description"):
        lines.append(f"  Seller's description: {item['description']}")
    return "\n".join(lines)


def _describe_wardrobe_item(item: dict) -> str:
    line = (
        f"- {item.get('name', 'Unnamed item')} ({item.get('category', 'unknown')}; "
        f"colors: {', '.join(item.get('colors') or []) or 'unspecified'}; "
        f"style: {', '.join(item.get('style_tags') or []) or 'unspecified'})"
    )
    if item.get("notes"):
        line += f" — {item['notes']}"
    return line


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return (
            "Can't write a fit card without an outfit: suggest_outfit didn't "
            "return anything to caption."
        )

    price = new_item.get("price")
    price_text = f"${price:.2f}" if isinstance(price, (int, float)) else "an unlisted price"
    platform = new_item.get("platform") or "a resale app"
    prompt = (
        f"The thrifted find:\n{_describe_item(new_item)}\n"
        f"  Price: {price_text}\n"
        f"  Platform: {platform}\n\n"
        f"How it's being styled:\n{outfit.strip()}\n\n"
        "Write a 2 to 4 sentence social media caption about this find, in first "
        "person, like a real person posting their outfit. Mention the item, the "
        f"price ({price_text}) and the platform ({platform}) exactly once each. "
        "Be specific about the vibe. Return only the caption."
    )
    response = generate(prompt, system=_CAPTION_SYSTEM)
    if response.strip():
        return response
    return (
        f"Thrifted this {new_item.get('title', 'piece')} for {price_text} on "
        f"{platform} and I'm obsessed."
    )


_CAPTION_SYSTEM = (
    "You write short, casual outfit captions for Instagram and TikTok. They "
    "sound like a real person, not a product listing. A hashtag or emoji or two "
    "is fine. No quotation marks around the caption."
)
