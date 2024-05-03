pwd=$(pwd)
root=${pwd%asian_math_pro*}asian_math_pro

# format code
pre-commit run --all-files

# run tests
cd "${root}" || exit
python3 -m unittest discover "$root"/test
