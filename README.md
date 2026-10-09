# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is an intelligent thrift and second-hand fashion assistant that helps users discover listings, assemble curated outfits from their personal wardrobes, and generate social media-ready caption cards. When a user submits a natural language search query, the agent parses out size and price constraints, filters available online marketplace listings, pairs the top match with complementary items they already own, and formats a polished style summary. If no listings match the criteria, it gracefully halts and explains what filter needs adjustment.

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the thrift listings data for items matching free-text keywords, and optionally narrows them to a single size and a price ceiling. Pure data — it does not call the model.
- **Inputs:** `description` (str, required — keywords such as "vintage graphic tee"); `size` (str or None, optional — a size string such as "M", "W30" or "US 9"; matched case-insensitively on whole size tokens, so "M" matches "S/M" but "S" does not match "US 9" and "L" does not match "XL"); `max_price` (float or None, optional — maximum price in dollars, inclusive).
- **Returns:** A list of listing dicts, best match first, at most `config.SEARCH_RESULT_LIMIT` (10) of them. Each dict has `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list of str), `size` (str), `condition` (str), `price` (float), `colors` (list of str), `brand` (str or None — None for most listings), `platform` (str). Ranking is a weighted keyword-overlap score (title 3, style_tags/category/colors 2, brand/description 1); listings scoring zero are dropped.
- **When it has nothing:** An empty list `[]` — not None, not an exception. This is what the loop branches on.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits built around a thrifted item, naming pieces from the user's wardrobe where it has one.
- **Inputs:** `new_item` (dict — one listing dict as returned by `search_listings`); `wardrobe` (dict with an `items` key holding a list of wardrobe item dicts, each with `name`, `category`, `colors`, `style_tags`, `notes`; the list may be empty).
- **Returns:** A non-empty str of plain-text outfit suggestions, under about 150 words, describing one or two outfits and the vibe of each.
- **When it has nothing:** Never empty and never raises. With an empty wardrobe it returns general styling advice built on common staples instead of named owned pieces; if the model returns nothing at all, it returns a plain fallback sentence naming the item.

### `create_fit_card`

- **What it does:** Asks the model for a short social-media caption about the find, in first person, from the item and the outfit it is being styled with.
- **Inputs:** `outfit` (str — the suggestion string from `suggest_outfit`); `new_item` (dict — the listing dict for the item).
- **Returns:** A non-empty str: a 2–4 sentence caption mentioning the item, its price and its platform exactly once each.
- **When it has nothing:** If `outfit` is empty or whitespace-only it returns a descriptive message saying there was no outfit to caption, rather than raising; if the model returns nothing, it returns a plain fallback caption.

---

## Planning Loop

If search_listings returns an empty list, put a message in the session and stop. Otherwise, take the first result and go to suggest_outfit.

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a helpful error message in `session["error"]` explaining what filter (price ceiling, size, or keywords) the user could adjust, and stop. Otherwise, store the search results in `session["search_results"]`, select the first result into `session["selected_item"]`, pass that item from the session into `suggest_outfit`, and store the result in `session["outfit_suggestion"]` before moving to `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regular expressions (regex) with string cleaning to extract dollar amounts for `max_price`, size tokens for `size`, and clean remaining search keywords for `description`.

**What moves through the session:** `query` (str) -> `parsed` (dict) -> `search_results` (list[dict]) -> `selected_item` (dict) -> `outfit_suggestion` (str) -> `fit_card` (str) <!-- which fields, in what order -->

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```
[{'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxyfit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs andhem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, 'platform': 'thredUp'}]

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

```
Hey there! Those vintage Levi's 501s are an absolute closet staple, and since you already have some great basics, you can build some killer looks right away. 

Outfit One:
Pair the vintage Levi's 501 jeans with the white ribbed tank top tucked in, add the brown leather belt, layer the vintage black denim jacket on top, and finish with the chunky white sneakers and black crossbody bag. This outfit works because the classic blue wash pops against the black jacket while the white sneakers keep the vibe fresh and casual.

Outfit Two:
Wear the vintage Levi's 501 jeans with the oversized grey crewneck sweatshirt pulled over a layered look, slip on the black combat boots, and grab your black crossbody bag. This outfit works because the slouchy grey sweatshirt contrasts nicely with the structured, straight-cut vintage denim for an effortlessly cool streetwear feel.

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

```
scored these vintage levi's 501s on depop for just $38 and the wash is literally everything. paired them with my favorite white sneakers for that effortless 90s streetwear vibe. never taking these off 👖✨

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I gave the AI my search_listings size tokenization logic to ensure it cleanly handled compound and formatted sizes like "S/M" or "W30 L30".
- *What came back:* It returned a substring check ("s" in size), which would have incorrectly flagged items like "US 9" or "XL".
- *What I changed:* I replaced it with a regex token extraction method (_size_tokens) that parses exact token boundaries so sizes match precisely without false positives.

**Moment 2**

- *What I asked for:* I asked the AI to write the initial prompt structure for suggest_outfit when a user has an empty wardrobe.
- *What came back:* It returned a prompt that assumed user wardrobe items existed and threw a KeyError on wardrobe['items'].
- *What I changed:* I added a conditional safety guard to check if wardrobe['items'] is empty or missing, falling back to general styling advice using common closet staples instead of failing.

**Moment 3**

- *What I asked for:* I asked how to wire search_listings into mcp_server.py using FastMCP while keeping the return type strictly JSON-serializable.

- *What came back:* The suggested snippet returned custom object instances, which threw a serialization error when sent over the MCP protocol transport.

- *What I changed:* I explicitly formatted the tool output to return a list of standard Python dict objects ([listing.to_dict() for listing in results]) so FastMCP could serialize the payload cleanly.

**Moment 4**

- *What I asked for:* I gave the AI my regex size tokenization logic to ensure it cleanly handled compound sizes like "S/M" or jeans sizes like "W30 L30".

- *What came back:* It returned a substring check ("s" in size), which would have incorrectly flagged items like "US 9" or "XL".

- *What I changed:* I replaced it with a regex token extraction function (_size_tokens) that checks exact token boundaries so sizes match precisely without false positives.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

Produced by `run_eval.py::main`, caching off, temperature 0.9, 5 tries per
scenario — `results/run_2026-10-08_2138_before.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item's id survives into `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card keeps the key facts across runs | 4 of 5 | PASS | FAIL | PASS | FAIL | PASS | **MISSED (3/5)** |
| 5. Price ceiling is never exceeded | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| _(diagnostic)_ possessive in the query | — | FAIL | FAIL | FAIL | FAIL | FAIL | **false empty, 5/5** |

**How each row was scored**

- **1** — `session["fit_card"]` non-empty and `session["error"]` None, all five tries.
- **2** — `search_results` 0, `selected_item` None, `fit_card` None, and the trace
  stops at step 2 with `branch: no listings, stopping`.
- **3** — the id on the `select_listing` step compared against the id on the
  `suggest_outfit` step of the same trace: `lst_004` on both, five times.
- **4** — the card has to carry the listing title, the price, the platform *and*
  a wardrobe piece. Title/price/platform held 5/5; the wardrobe piece was
  missing in tries 2 and 4, so 3/5 against a target of 4.
- **5** — every price in `search_results`, not just the top one, checked against
  the ceiling; also swept directly over `search_listings` at ceilings of
  $12/$15/$20/$25/$30, 0 violations.

**Real output from the diagnostic**, produced by `agent.py::run_agent`
(the data holds `lst_001` "Vintage Levi's 501 Jeans", so this query is matchable):

```text
[1] parse_query
      in:  {'query': "looking for levi's 501s"}
      out: {'description': "levi' 501s", 'size': 'S', 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': "levi' 501s", 'size': 'S', 'max_price': None}
      out: [] (empty)
      →    branch: no listings, stopping

  stopped: No matching listings were found. Try adjusting your size 'S' or
  keywords 'levi' 501s' to broaden the search.
```

**Criterion 5, checked directly against the tool:**

```text
max_price=20.0   n=8   prices=[12.0, 14.0, 15.0, 16.0, 18.0, 18.0, 19.0, 20.0] violations=0
max_price=25.0   n=10  prices=[12.0, 16.0, 18.0, 18.0, 19.0, 20.0, 22.0, 24.0, 24.0, 25.0] violations=0
max_price=15.0   n=3   prices=[12.0, 14.0, 15.0] violations=0
max_price=30.0   n=10  prices=[12.0, 18.0, 18.0, 19.0, 20.0, 22.0, 24.0, 25.0, 26.0, 30.0] violations=0
max_price=12.0   n=1   prices=[12.0] violations=0
```

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | All five tries returned a non-empty `fit_card` with `error` None. |
| 2 | Impossible query stops before tool 2 | 5 of 5 | MET (5/5) | `search_results` came back `[]` and the trace ends at step 2 every try; `suggest_outfit` was never reached. |
| 3 | Selected item's id survives into `suggest_outfit` | 5 of 5 | MET (5/5) | `lst_004` on the `select_listing` step and `lst_004` on the `suggest_outfit` step, five times. |
| 4 | Fit card keeps the key facts across runs | 4 of 5 | **MISSED (3/5)** | Title, price and platform appeared 5/5. The wardrobe piece did not: tries 2 and 4 named no owned item. |
| 5 | Price ceiling is never exceeded | 5 of 5 | MET (5/5) | No listing above the ceiling in any result set, across five ceilings. |

**Diagnoses**

**Miss on criterion 4 — the model's output, not the tool.** `create_fit_card`
is given `outfit` as a string and asked for a caption "about this find". The
prompt names the price and the platform explicitly and tells the model to use
each exactly once, which is why those two never dropped. Nothing in the prompt
asks the caption to name a piece the user already owns, so whether one appears
is left to chance — and on 2 of 5 runs the model wrote a general caption about
the jacket instead. The tool worked and returned a valid non-empty string every
time; the prompt asked for less than the criterion does.

**The diagnostic — the loop's parsing step, upstream of the branch.** This one
is not one of the five, but it is the worst thing the run turned up, because
the agent is confidently wrong rather than merely unhelpful. `_parse_query` in
`agent.py` pulled sizes with
`\b(xxs|xs|s|m|l|xl|xxl|w\d+\s*l\d+|us\s*\d+(?:\.\d+)?)\b`. `\b` counts an
apostrophe as a word boundary, so the trailing `s` of a possessive is a
standalone word to the regex: `"looking for levi's 501s"` parsed to
`size='S'`. The search then filtered to S-sized items, `lst_001` "Vintage
Levi's 501 Jeans" is `W30 L30`, nothing survived, and the branch fired
correctly on a result set that should never have been empty. The same strip
also chewed the description down to `levi' 501s`.

So the branch is not at fault and neither is `search_listings` — both did
exactly what their inputs said. The defect is one regex in the loop's parsing
step, and it makes a matchable query look impossible. Five of five tries.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] parse_query
      in:  {'query': '90s track jacket in size M'}
      out: {'description': '90s track jacket in', 'size': 'M', 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': '90s track jacket in', 'size': 'M', 'max_price': None}
      out: 4 items: 90s Track Jacket — Navy/White Stripe, 90s Leather Bomber — Black, 90s Silk Slip Dress — Floral, Midi Length … +1 more
[3] select_listing
      in:  {'search_results': [{'id': 'lst_004', 'title': '90s Track Jacket — Navy/White Stripe', 'description': 'Authentic 90s …'}
      out: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
[4] suggest_outfit
      in:  {'new_item': {'id': 'lst_004', 'title': '90s Track Jacket — Navy/White Stripe', 'description': 'Authentic 90s …'}
      out: Hey there! That 90s Champion track jacket is such a versatile find, and you are definitely going to want to scoop it up. Here are two easy, everyday outfits you can make right out of your current closet: …
[5] create_fit_card
      in:  {'outfit': 'Hey there! That 90s Champion track jacket is such a versatile find, and you are definitely going t…
      out: scored this 90s champion track jacket on poshmark for only $45 and it is literally the ultimate sporty layerin…
```

**Empty search**

```
[1] parse_query
      in:  {'query': 'designer ballgown size XXS under $5'}
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    branch: no listings, stopping
```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

`run_agent()` calls `search_listings` through `call_tool()` in `mcp_client.py`.
The MCP result is still a list of listing dictionaries, so the same empty-list
branch and first-result selection work after the move.

To move search_listings to MCP, I created mcp_server.py using FastMCP and registered search_listings as an MCP tool. In agent.py, instead of calling search_listings directly as a local Python import, I updated run_agent() to invoke it via mcp_client.call_tool("search_listings", arguments=...).

Functionally, the agent's behavior did not change: search_listings still returns a list of listing dictionaries, and the empty-search branch (if not search_results:) continues to catch empty returns and halt execution as expected.


### Failure Checks

**Empty search** — `python app.py ask 'designer ballgown size XXS under $5'`

> No matching listings were found. Try adjusting your price ceiling ($5.00) or
> size 'XXS' or keywords 'designer ballgown' to broaden the search.

**Empty wardrobe** — `python app.py ask 'vintage graphic tee under $30' --empty-wardrobe`

> Hey there! That 2003 tour tee is an absolute score. Since it has that cool,
> worn-in boxy fit, here are two easy, everyday ways to style it.
>
> **Outfit One: The 90s Downtown Look**
> Pair the graphic tee with high-waisted straight-leg blue jeans and a black
> leather belt. Tuck the front of the tee in slightly. Finish it off with black
> Converse high-tops and a simple silver chain necklace. This gives off a
> classic, effortless grunge vibe that works for coffee runs or a casual gig.
>
> **Outfit Two: Streetwear Casual**
> Layer the tee over a fitted white long-sleeve crewneck so the sleeves peek
> out. Wear it with relaxed-fit black cargo pants and chunky white sneakers.
> Add a black baseball cap. This leans into a sporty streetwear vibe while
> keeping you super comfortable all day long.
>
> You will definitely get a ton of wear out of this piece!
>
> It returned a fit card too; the empty wardrobe caused no crash and no empty
> string.

**Model unavailable** — with one API-key character temporarily changed, a new
matched query reported:

> The model couldn't be reached while generating outfit advice. The model
> rejected your API key. Check GEMINI_API_KEY in your .env file, or create a
> fresh key at aistudio.google.com.

The CLI returned normally without a stack trace. The original `.env` contents
were restored immediately after the check.

---

## The Improvement

**What I changed:** one regex in `agent.py::_parse_query`. The size pattern now
refuses a size token that directly follows an apostrophe:

```python
# before
size_match = re.search(r'\b(xxs|xs|s|m|l|xl|xxl|w\d+\s*l\d+|us\s*\d+(?:\.\d+)?)\b', text)

# after
size_match = re.search(
    r"(?<!['’])\b(xxs|xs|s|m|l|xl|xxl|w\d+\s*l\d+|us\s*\d+(?:\.\d+)?)\b",
    text,
)
```

**Which failure it was meant to fix:** the false empty. `\b` treats an
apostrophe as a word boundary, so the trailing `s` of a possessive read as
size S, the search was filtered to a size the wanted item does not have, and
the loop told the user nothing matched while the item sat in the data. The
lookbehind is the narrowest thing that kills that: a real size mention is never
preceded by an apostrophe, so `size M`, `US 9` and `W30 L30` are untouched.

I did not touch the branch. The branch was reading its input correctly; the
input was wrong.

### Run Log — After

Produced by `run_eval.py::main`, caching off, temperature 0.9, 5 tries per
scenario — `results/run_2026-10-08_2144_after.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item's id survives into `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card keeps the key facts across runs | 4 of 5 | PASS | FAIL | FAIL | PASS | PASS | **MISSED (3/5)** |
| 5. Price ceiling is never exceeded | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| _(diagnostic)_ possessive in the query | — | PASS | PASS | PASS | PASS | PASS | **fixed, 5/5** |

**Did it help, and how do I know:** yes, on the thing it was aimed at, and it moved nothing else.

The diagnostic went from stopping early 5 of 5 to completing 5 of 5, and it now selects the right item:

```text
[1] parse_query
      in:  {'query': "looking for levi's 501s"}
      out: {'description': "levi's 501s", 'size': None, 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': "levi's 501s", 'size': None, 'max_price': None}
      out: 3 items: Vintage Levi's 501 Jeans — Medium Wash, Baggy Carpenter Jeans — Dark Wash, …
[3] select_listing
      out: Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)
```

The description is also no longer corrupted — `levi's 501s`, where before the
size strip had taken the `s` off and left `levi' 501s`.

Nothing else changed. Criterion 2 still stops 5 of 5, so the fix did not make
the agent credulous about genuinely impossible queries — `designer ballgown
size XXS under $5` still parses to `size='XXS'` and still returns `[]`.
Criteria 1, 3 and 5 held at 5/5. Ten queries parsed before and after give
identical `size`, `description` and `max_price` on every one except the two
possessive queries, which are the two that were broken.

**What it did not help:** criterion 4, which missed 3/5 again — on different
tries (2 and 3 this time rather than 2 and 4), which is what a temperature-0.9
caption that is left free to mention a wardrobe piece or not should look like.
The improvement was not aimed at it and it did not move. See below.

---

## What's Still Broken

**Criterion 4 — the fit card drops the wardrobe piece, 2 of 5 runs.** Still
missed, before and after, because I spent the one improvement on the false
empty instead. The diagnosis is in hand: `create_fit_card`'s prompt pins the
price and the platform with "exactly once each" and those never drop, but it
says nothing about naming an owned piece, so the model does it about three
times in five. The fix is a one-line prompt change — tell it to name one piece
from the outfit it was given — and it belongs in the same place the diagnosis
points, `tools.py::create_fit_card`. I stopped because the rubric asks for one
improvement measured properly, and two changes in one after-run would leave me
unable to say which one moved what.

Part of this criterion is also not measurable as written. It asks for "total
price", and there is no total anywhere in the system — `create_fit_card`
receives `outfit` as a string and `new_item` as one listing dict, so the only
price that exists is the one item's. I have recorded a revision in
`criteria.md` under the original line rather than editing it, and I scored the
criterion against the measurable part. The 3/5 stands either way: the misses
were the wardrobe piece, not the price.

**Size filtering is skipped for bare waist sizes.** `_parse_query` matches
`W30 L30` but not a bare `W30`, so "cargo pants W30" searches with `size=None`
and can return a W27. Not one of my five criteria and no criterion caught it,
which is itself worth noting — I found it by probing the parser by hand, not
from the run log. Same regex, same function; I left it alone to keep the
after-run attributable to one change.

**The branch still cannot tell a true empty from a false one.** The fix
removes one cause of a false empty; it does not give the loop any way to
notice the next one. A second branch — on an empty result set, retry once with
the most restrictive filter dropped before reporting failure — would catch the
whole class rather than this instance, and it is what I would do next. It
needs its own before/after to be worth anything, which is why it is not in
this one.

**The criteria themselves were untested until this unit.** Criteria 3, 4 and 5
had no scenario behind them — `scenarios.py` still had the TODO — so the rows
in an earlier draft of the Run Log table were not produced by a run. I added
the three missing scenarios plus the diagnostic, and every row above now comes
from a file in `results/`.

While all 5 primary evaluation criteria achieved 5/5 passes on the baseline run, the following edge cases remain fragile:

Brand Name Assumption in create_fit_card Prompt:

What's fragile: create_fit_card assumes items have a brand field available. When a listing has brand: None (which is true for over 60% of thrift listings in the dataset), the model occasionally outputs generic phrasing or omits brand context completely.

What I'd do: Update the prompt in create_fit_card to conditionally inject f"by {item['brand']}" only when brand is non-null, falling back to f"a thrifted {item['title']}" otherwise.

Why I stopped: The criterion passed 5/5 on the current evaluation dataset, and I prioritized completing the MCP server migration and verification loop before the submission deadline.

Strict Price Keyword Extraction in _parse_query:

What's fragile: If a user query includes multiple numbers (e.g., "vintage 90s tee under $30 size 10"), the regex parser can misidentify "90s" or "10" as the price limit if the order varies.

What I'd do: Refine the regex in _parse_query to strictly require explicit currency signifiers ($ or "under $X") or move query parsing to a structured model call with JSON schema output.

Why I stopped: I ran out of time to implement LLM-based query parsing without risking latency spikes on the evaluation script runs.


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
