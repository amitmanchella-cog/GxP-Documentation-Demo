# ER-CHG-4127 — Executed test results
**System / version:** Stability Sample Tracker 3.5.0 (Draft change CHG-4127) · **Commit SHA:** `600fd97c90d80ec4990c773cb5d588a4cd948c4b` (PR head; CI executes the PR merge ref `0c0f4f8` = `600fd97` merged into `main` `f28a790`) · **CI run:** https://github.com/amitmanchella-cog/GxP-Documentation-Demo/actions/runs/41239870984 / job ID `124651363065` · **Executed (UTC):** 2026-10-31T20:38:49Z–20:39:07Z · **Executed by:** CI (GitHub Actions)

## Summary
125 passed, 0 failed, 0 skipped, 0 xfailed; coverage 93.72% (gate 85%); `ruff check .` and `ruff format --check .` clean. Includes TS-005 (`tests/test_amend.py`, `tests/test_amend_boundaries.py`) and TS-006 (`tests/test_amend_audit.py`).

## Console output (verbatim, unedited)
Excerpt of the job log, fetched from GitHub Actions, for the checkout, lint, format and test steps (job log lines copied without modification):
```
2026-10-31T20:38:51.5616117Z [command]/usr/bin/git config --local --unset-all extensions.worktreeConfig
2026-10-31T20:38:51.5651548Z ##[group]Checking out the ref
2026-10-31T20:38:51.5758102Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/6/merge
2026-10-31T20:38:51.5775851Z Note: switching to 'refs/remotes/pull/6/merge'.
2026-10-31T20:38:51.5776749Z 
2026-10-31T20:38:51.5777497Z You are in 'detached HEAD' state. You can look around, make experimental
2026-10-31T20:38:51.5779270Z changes and commit them, and you can discard any commits you make in this
2026-10-31T20:38:51.5781236Z state without impacting any branches by switching back to a branch.
2026-10-31T20:38:51.5783251Z 
2026-10-31T20:38:51.5784526Z If you want to create a new branch to retain commits you create, you may
2026-10-31T20:38:51.5786196Z do so (now or later) by using -c with the switch command. Example:
2026-10-31T20:38:51.5787114Z 
2026-10-31T20:38:51.5787517Z   git switch -c <new-branch-name>
2026-10-31T20:38:51.5788149Z 
2026-10-31T20:38:51.5788608Z Or undo this operation with:
2026-10-31T20:38:51.5789372Z 
2026-10-31T20:38:51.5789880Z   git switch -
2026-10-31T20:38:51.5790502Z 
2026-10-31T20:38:51.5791434Z Turn off this advice by setting config variable advice.detachedHead to false
2026-10-31T20:38:51.5792799Z 
2026-10-31T20:38:51.5794807Z HEAD is now at 0c0f4f8 Merge 600fd97c90d80ec4990c773cb5d588a4cd948c4b into f28a790c3ad768d5227c3726eb45b57daa158815
2026-10-31T20:39:00.1738930Z ##[group]Run ruff check .
2026-10-31T20:39:00.1739230Z [36;1mruff check .[0m
2026-10-31T20:39:00.1770914Z shell: /usr/bin/bash -e {0}
2026-10-31T20:39:00.1771160Z env:
2026-10-31T20:39:00.1771427Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.1771874Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib/pkgconfig
2026-10-31T20:39:00.1772306Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.1772700Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.1773082Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.1773466Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib
2026-10-31T20:39:00.1774156Z ##[endgroup]
2026-10-31T20:39:00.1921148Z All checks passed!
2026-10-31T20:39:00.1966780Z ##[group]Run ruff format --check .
2026-10-31T20:39:00.1967099Z [36;1mruff format --check .[0m
2026-10-31T20:39:00.1996949Z shell: /usr/bin/bash -e {0}
2026-10-31T20:39:00.1997196Z env:
2026-10-31T20:39:00.1997465Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.1997900Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib/pkgconfig
2026-10-31T20:39:00.1998316Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.1998697Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.1999072Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.1999450Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib
2026-10-31T20:39:00.1999765Z ##[endgroup]
2026-10-31T20:39:00.2149745Z 39 files already formatted
2026-10-31T20:39:00.2200742Z ##[group]Run mkdir -p reports && set -o pipefail && pytest --junitxml=reports/junit.xml --cov-report=xml:reports/coverage.xml | tee reports/pytest.txt
2026-10-31T20:39:00.2201835Z [36;1mmkdir -p reports && set -o pipefail && pytest --junitxml=reports/junit.xml --cov-report=xml:reports/coverage.xml | tee reports/pytest.txt[0m
2026-10-31T20:39:00.2233581Z shell: /usr/bin/bash -e {0}
2026-10-31T20:39:00.2233838Z env:
2026-10-31T20:39:00.2234382Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.2234837Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib/pkgconfig
2026-10-31T20:39:00.2235268Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.2235651Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.2236093Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:39:00.2236791Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib
2026-10-31T20:39:00.2237306Z ##[endgroup]
2026-10-31T20:39:04.8352472Z ........................................................................ [ 57%]
2026-10-31T20:39:06.4256730Z .....................................................                    [100%]
2026-10-31T20:39:06.4257718Z =============================== warnings summary ===============================
2026-10-31T20:39:06.4258718Z ../../../../../opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/site-packages/starlette/testclient.py:37
2026-10-31T20:39:06.4260690Z   /opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/site-packages/starlette/testclient.py:37: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
2026-10-31T20:39:06.4262608Z     _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]
2026-10-31T20:39:06.4263287Z 
2026-10-31T20:39:06.4263678Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-10-31T20:39:06.4264718Z ================================ tests coverage ================================
2026-10-31T20:39:06.4265678Z _______________ coverage: platform linux, python 3.12.15-final-0 _______________
2026-10-31T20:39:06.4266258Z 
2026-10-31T20:39:06.4266438Z Name              Stmts   Miss  Cover   Missing
2026-10-31T20:39:06.4266926Z -----------------------------------------------
2026-10-31T20:39:06.4267366Z sst/__init__.py       1      0   100%
2026-10-31T20:39:06.4267783Z sst/audit.py         16      1    94%   34
2026-10-31T20:39:06.4268280Z sst/db.py            33     10    70%   58-59, 63-69, 84
2026-10-31T20:39:06.4268793Z sst/main.py         227      5    98%   44-46, 58, 266
2026-10-31T20:39:06.4269261Z sst/regimes.py       42      0   100%
2026-10-31T20:39:06.4269686Z sst/rounding.py      23      0   100%
2026-10-31T20:39:06.4270198Z sst/seed.py         104     12    88%   165, 211, 236, 242, 295-301, 305
2026-10-31T20:39:06.4270754Z -----------------------------------------------
2026-10-31T20:39:06.4271195Z TOTAL               446     28    94%
2026-10-31T20:39:06.4272009Z Coverage XML written to file reports/coverage.xml
2026-10-31T20:39:06.4272616Z Required test coverage of 85% reached. Total coverage: 93.72%
2026-10-31T20:39:06.4273195Z 125 passed, 1 warning in 4.48s
```

## Attached artefacts
`test-evidence` artifact (`junit.xml`, `coverage.xml`, `pytest.txt`): https://github.com/amitmanchella-cog/GxP-Documentation-Demo/actions/runs/41239870984/artifacts/13057585003 (SHA256 of zip `0edeba71db041a63ad10aba9984904455316340e55a1d620e3d483892e9c9a24`)

Any later commits that change only this ER file or the RTM/CC trace fields are listed with their CI runs in the closing PR comment.
