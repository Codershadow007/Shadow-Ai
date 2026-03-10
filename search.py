from ddgs import DDGS

def web_search(query, max_results=4):

    query = query.lower().strip()

    results = []

    try:
        with DDGS() as ddgs:
            raw = ddgs.text(
                query,
                region="in-en",
                safesearch="off",
                max_results=max_results
            )

            for r in raw:
                results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "link": r.get("href", "")
                })

    except Exception as e:
        print("SEARCH ERROR:", e)

    print("FINAL RESULTS:", results)

    return results