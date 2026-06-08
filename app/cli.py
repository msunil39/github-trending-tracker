import argparse
from database import init_db, fetch_repos, fetch_top_by_stars, fetch_history, fetch_stats


def print_repos(repos: list):
    if not repos:
        print("No repos found.")
        return
    print(f"\n{'#':<4} {'Repo':<45} {'Language':<15} {'Stars Today':<12} {'Total Stars'}")
    print("-" * 95)
    for r in repos:
        print(f"{r.get('rank', '-'):<4} {r['full_name']:<45} {r['language'] or 'N/A':<15} "
              f"{r['stars_today']:<12} {r['total_stars']}")


def main():
    init_db()
    parser = argparse.ArgumentParser(description="GitHub Trending Tracker CLI")
    parser.add_argument("--language", type=str, help="Filter repos by language")
    parser.add_argument("--top",      type=int, help="Show top N repos by stars today")
    parser.add_argument("--history",  type=str, help="Show history for a repo e.g. owner/repo")
    parser.add_argument("--stats",    action="store_true", help="Show database stats")
    parser.add_argument("--limit",    type=int, default=20, help="Number of results (default 20)")

    args = parser.parse_args()

    if args.stats:
        stats = fetch_stats()
        print(f"\nTotal records : {stats['total_records']}")
        print("\nBy language:")
        for lang, count in stats["by_language"].items():
            print(f"  {lang:<20} {count}")
        print("\nTop today:")
        for item in stats["top_today"]:
            print(f"  {item['repo']:<45} +{item['stars_today']} stars")

    elif args.top:
        repos = fetch_top_by_stars(limit=args.top)
        print(f"\nTop {args.top} repos by stars today:")
        print_repos(repos)

    elif args.history:
        history = fetch_history(args.history)
        if not history:
            print(f"No history found for '{args.history}'")
        else:
            print(f"\nHistory for {args.history}:")
            print(f"{'Date':<25} {'Stars Today':<12} {'Total Stars'}")
            print("-" * 50)
            for r in history:
                print(f"{r['scraped_at']:<25} {r['stars_today']:<12} {r['total_stars']}")

    elif args.language:
        repos = fetch_repos(language=args.language, limit=args.limit)
        print(f"\nTrending repos for language: {args.language}")
        print_repos(repos)

    else:
        repos = fetch_repos(limit=args.limit)
        print("\nLatest trending repos (all languages):")
        print_repos(repos)


if __name__ == "__main__":
    main()
