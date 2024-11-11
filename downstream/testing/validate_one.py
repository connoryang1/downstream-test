import argparse
import subprocess
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Test a target downstream algorithm function implementation "
            "against a reference implementation over a large test case battery."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "command",
        help="The command to test. Example: 'python3 ./my_program'",
    )
    parser.add_argument(
        "target",
        help=(
            "The algorithm function to test. "
            "Example: 'steady_algo.assign_storage_site'"
        ),
    )
    parser.add_argument(
        "--reference",
        default="python3 -O -m downstream",
        help="Reference command to validate against.",
    )
    args = parser.parse_args()

    script = r"""
set -e

printf "Smoke testing $1 $3... "
: | $1 $3
echo 8 0 | $1 $3

printf "Smoke testing $2 $3... "
: | $2 $3
echo 8 0 | $2 $3

echo "Comparing $1 $3 to $2 $3..."
badline="$( \
    cmp <( \
            python3 -O -m downstream.testing.generate \
            | $(which pv && echo "--size $((840*1024))" || which cat) \
            | $1 $3 \
        ) \
        <( \
            python3 -O -m downstream.testing.generate \
            | $2 $3 \
        ) \
    | awk '{print $NF}' \
)"

if [ -n "${badline}" ]; then
    sleep 1
    echo "Tests failed on line ${badline}"
    inline=$(python3 -m downstream.testing.generate | head -n "${badline}" | tail -n 1)
    S=$(echo "${inline}" | cut -d ' ' -f 1)
    T=$(echo "${inline}" | cut -d ' ' -f 2)
    echo "S=${S}, T=${T}"

    aline="$(python3 -m downstream.testing.generate | $1 $3 | head -n "${badline}" | tail -n 1)"
    echo "python3 -m downstream $3"
    echo ">>> ${aline}"

    bline="$(python3 -m downstream.testing.generate | $2 $3 | head -n "${badline}" | tail -n 1)"
    echo "$2 $3"
    echo ">>> ${bline}"

    exit 1
else
    echo "Test passed!"
    exit 0
fi
"""

    result = subprocess.run(
        [
            "bash",
            "-c",
            script,
            sys.argv[0],
            args.reference,
            args.command,
            args.target,
        ],
    )
    sys.exit(result.returncode)
