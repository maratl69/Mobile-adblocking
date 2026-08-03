import requests
import sys
import time

def fetch_with_retry(url, retries=3, timeout=20):
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": "filter-merger/1.0"})
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"  Tentativo {attempt}/{retries} fallito per {url}: {e}", file=sys.stderr)
            if attempt < retries:
                time.sleep(2 * attempt)
    return None

def main():
    src_file, out_file, title = sys.argv[1], sys.argv[2], sys.argv[3]

    with open(src_file) as f:
        urls = [u.strip() for u in f if u.strip() and not u.startswith("#")]

    lines = [
        f"! Title: {title}",
        "! Expires: 6 hours",
        f"! Sources merged: {len(urls)}",
        ""
    ]

    ok, failed = 0, []

    for url in urls:
        print(f"Scarico: {url}")
        content = fetch_with_retry(url)
        if content is None:
            failed.append(url)
            lines.append(f"\n! --- SKIPPED (fetch failed): {url} ---")
            continue
        lines.append(f"\n! --- Source: {url} ---")
        lines.append(content)
        ok += 1

    with open(out_file, "w") as f:
        f.write("\n".join(lines))

    print(f"\nCompletate: {ok}/{len(urls)}")
    if failed:
        print("Fallite:", *failed, sep="\n  - ", file=sys.stderr)
        # non blocchiamo il workflow: meglio un file parziale che nessun aggiornamento
        # se vuoi che fallisca il job quando una lista salta, decommenta:
        # sys.exit(1)

if __name__ == "__main__":
    main()
