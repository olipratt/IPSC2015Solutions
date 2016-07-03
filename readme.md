# IPSC 2015 Solutions

Solutions to problems listed [here](https://ipsc.ksp.sk/2015/problems).

## Problem A

Solutions to [Problem A](https://ipsc.ksp.sk/2015/real/problems/a.html) are found by running `ipsc2015a.py`.

Run with no arguments to solve sub-problem `g1`, run with any argument to solve sub-problem `g2`. The program asserts the results are correct by matching to the output values in the `.out` files.

## Problem G

Solutions to [Problem G](https://ipsc.ksp.sk/2015/real/problems/g.html) are found by running `ipsc2015g.py`.

Run with no arguments to solve sub-problem `g1`, run with any argument to solve sub-problem `g2` - however `g2` requires you to run `problem2015g/g2gen.py` to produce the input file first. The program asserts the results are correct by matching to the output values in the `.out` files.

Solves individual inputs for `g2` in reasonable times when run under `pypy`, but definite room for improvement:

1. ~90s
2. ~15 mins
3. ~5 mins
4. ~90s
5. ~80s

`g1` solves entirely in about 1s.
