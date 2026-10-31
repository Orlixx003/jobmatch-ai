"""Command-line interface for JobMatch AI.

Example:
    python cli.py --cv examples/cv_example.txt --job examples/job_example.txt --lang pl
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from jobmatch import analyze_match, read_cv


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Compare a CV with a job offer using Claude.")
    parser.add_argument("--cv", required=True, help="Path to CV (.pdf, .docx, .txt, .md)")
    parser.add_argument("--job", required=True, help="Path to a text file with the job offer")
    parser.add_argument("--lang", default="en", choices=["pl", "en", "uk"], help="Output language")
    parser.add_argument("--out", help="Save the report as Markdown to this path")
    args = parser.parse_args()

    try:
        cv_text = read_cv(args.cv)
        job_text = Path(args.job).read_text(encoding="utf-8")
        result = analyze_match(cv_text, job_text, args.lang)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    report = result.to_markdown()
    print(report)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"Saved to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
