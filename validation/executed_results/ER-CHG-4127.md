# ER-CHG-4127 — Executed test results, CHG-4127 (PR #5)
**System / version:** SST 3.4.1 (target 3.5.0, see finding 10) · **Commit SHA:** `43da149adc9cb2738bf7905dfd2fa3b98ac88533` · **CI run:** https://github.com/amitmanchella-cog/GxP-Documentation-Demo/actions/runs/41238179614/job/124646264910 (run 41238179614, job 124646264910, workflow `CI`, job `test`) · **Executed (UTC):** 2026-10-31T20:17:09Z – 2026-10-31T20:17:27Z · **Executed by:** CI (GitHub Actions, ubuntu-26.04, Python 3.12.15) · **Conclusion:** success

`43da149` is the last commit on the PR branch that changes code (`sst/`) or tests (`tests/`). Commits after it change only `validation/` documents (this record, RTM and CC placeholders); the CI runs on those commits are listed in the closing comment on PR #5 and in CC-CHG-4127 §4a.

Scope: TS-002, TS-003, TS-004 (regression), TS-005 (`tests/test_amend.py`), TS-006 (`tests/test_amend_audit.py`); traceability in `validation/RTM.md` (URS-010, URS-011 and changed rows).

## Summary
Copied from the console output below:
```
Required test coverage of 85% reached. Total coverage: 93.57%
62 passed, 1 warning in 2.56s
```

## Console output (verbatim, unedited)
Full job log as returned by the GitHub Actions job-logs API for job 124646264910 (sha256 of the retrieved log file: `54946e09b99e295da239ed1a60405046a52ff892013bc70efdd69b5a959922ce`).
```
﻿2026-10-31T20:17:10.4700474Z Current runner version: '2.338.2'
2026-10-31T20:17:10.4725423Z ##[group]Runner Image Provisioner
2026-10-31T20:17:10.4726284Z Hosted Compute Agent
2026-10-31T20:17:10.4726976Z Version: 20261021.618
2026-10-31T20:17:10.4727618Z Commit: 21505ad2541d5be6135ed84fc33697146cf75b8e
2026-10-31T20:17:10.4728394Z Build Date: 2026-10-21T00:45:21Z
2026-10-31T20:17:10.4729143Z Worker ID: {a54b14d2-4194-460e-946f-22638f56be23}
2026-10-31T20:17:10.4729864Z Region: northcentralus
2026-10-31T20:17:10.4730498Z Cloud: Azure
2026-10-31T20:17:10.4731048Z ##[endgroup]
2026-10-31T20:17:10.4732502Z ##[group]Operating System
2026-10-31T20:17:10.4733273Z Ubuntu
2026-10-31T20:17:10.4734048Z 26.04.1
2026-10-31T20:17:10.4734647Z LTS
2026-10-31T20:17:10.4735172Z ##[endgroup]
2026-10-31T20:17:10.4735731Z ##[group]Runner Image
2026-10-31T20:17:10.4736438Z Image: ubuntu-26.04
2026-10-31T20:17:10.4737016Z Version: 20261025.179.1
2026-10-31T20:17:10.4738373Z Included Software: https://github.com/actions/runner-images/blob/ubuntu26/20261025.179/images/ubuntu/Ubuntu2604-Readme.md
2026-10-31T20:17:10.4739907Z Image Release: https://github.com/actions/runner-images/releases/tag/ubuntu26%2F20261025.179
2026-10-31T20:17:10.4740976Z ##[endgroup]
2026-10-31T20:17:10.4742167Z ##[group]GITHUB_TOKEN Permissions
2026-10-31T20:17:10.4744388Z Contents: read
2026-10-31T20:17:10.4745005Z Metadata: read
2026-10-31T20:17:10.4745671Z Packages: read
2026-10-31T20:17:10.4746288Z ##[endgroup]
2026-10-31T20:17:10.4748333Z Secret source: Actions
2026-10-31T20:17:10.4749383Z Cache mode: write
2026-10-31T20:17:10.4750087Z Prepare workflow directory
2026-10-31T20:17:10.5205428Z Prepare all required actions
2026-10-31T20:17:10.5279601Z Getting action download info
2026-10-31T20:17:10.7448334Z Download action repository 'actions/checkout@v4' (SHA:11d5960a326750d5838078e36cf38b85af677262)
2026-10-31T20:17:10.8338179Z Download action repository 'actions/setup-python@v5' (SHA:a26af69be951a213d495a4c3e4e4022e16d87065)
2026-10-31T20:17:10.8935061Z Download action repository 'actions/upload-artifact@v4' (SHA:ea165f8d65b6e75b540449e92b4886f43607fa02)
2026-10-31T20:17:11.0875983Z Complete job name: test
2026-10-31T20:17:11.1856478Z ##[group]Run actions/checkout@v4
2026-10-31T20:17:11.1857541Z with:
2026-10-31T20:17:11.1858193Z   repository: amitmanchella-cog/GxP-Documentation-Demo
2026-10-31T20:17:11.1862685Z   token: ***
2026-10-31T20:17:11.1863153Z   ssh-strict: true
2026-10-31T20:17:11.1863625Z   ssh-user: git
2026-10-31T20:17:11.1864410Z   persist-credentials: true
2026-10-31T20:17:11.1864929Z   clean: true
2026-10-31T20:17:11.1865390Z   sparse-checkout-cone-mode: true
2026-10-31T20:17:11.1865939Z   fetch-depth: 1
2026-10-31T20:17:11.1866382Z   fetch-tags: false
2026-10-31T20:17:11.1866850Z   show-progress: true
2026-10-31T20:17:11.1867315Z   lfs: false
2026-10-31T20:17:11.1867751Z   submodules: false
2026-10-31T20:17:11.1868227Z   set-safe-directory: true
2026-10-31T20:17:11.1868765Z   allow-unsafe-pr-checkout: false
2026-10-31T20:17:11.1869658Z ##[endgroup]
2026-10-31T20:17:11.4610268Z Syncing repository: amitmanchella-cog/GxP-Documentation-Demo
2026-10-31T20:17:11.4613589Z ##[group]Getting Git version info
2026-10-31T20:17:11.4615582Z Working directory is '/home/runner/work/GxP-Documentation-Demo/GxP-Documentation-Demo'
2026-10-31T20:17:11.4618005Z [command]/usr/bin/git version
2026-10-31T20:17:11.4619107Z git version 2.56.0
2026-10-31T20:17:11.4653283Z ##[endgroup]
2026-10-31T20:17:11.4660709Z Temporarily overriding HOME='/home/runner/work/_temp/17ebe4c2-a930-46c4-bb51-038075172190' before making global git config changes
2026-10-31T20:17:11.4663285Z Adding repository directory to the temporary git global config as a safe directory
2026-10-31T20:17:11.4667410Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/GxP-Documentation-Demo/GxP-Documentation-Demo
2026-10-31T20:17:11.4740894Z Deleting the contents of '/home/runner/work/GxP-Documentation-Demo/GxP-Documentation-Demo'
2026-10-31T20:17:11.4745362Z ##[group]Initializing the repository
2026-10-31T20:17:11.4751488Z [command]/usr/bin/git init /home/runner/work/GxP-Documentation-Demo/GxP-Documentation-Demo
2026-10-31T20:17:11.4889925Z hint: Using 'master' as the name for the initial branch. This default branch name
2026-10-31T20:17:11.4891928Z hint: will change to "main" in Git 3.0. To configure the initial branch name
2026-10-31T20:17:11.4893428Z hint: to use in all of your new repositories, which will suppress this warning,
2026-10-31T20:17:11.4895117Z hint: call:
2026-10-31T20:17:11.4896048Z hint:
2026-10-31T20:17:11.4897007Z hint: 	git config --global init.defaultBranch <name>
2026-10-31T20:17:11.4897706Z hint:
2026-10-31T20:17:11.4898658Z hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
2026-10-31T20:17:11.4899732Z hint: 'development'. The just-created branch can be renamed via this command:
2026-10-31T20:17:11.4900543Z hint:
2026-10-31T20:17:11.4901130Z hint: 	git branch -m <name>
2026-10-31T20:17:11.4902151Z hint:
2026-10-31T20:17:11.4903421Z hint: Disable this message with "git config set advice.defaultBranchName false"
2026-10-31T20:17:11.4907206Z Initialized empty Git repository in /home/runner/work/GxP-Documentation-Demo/GxP-Documentation-Demo/.git/
2026-10-31T20:17:11.4930261Z [command]/usr/bin/git remote add origin https://github.com/amitmanchella-cog/GxP-Documentation-Demo
2026-10-31T20:17:11.4980467Z ##[endgroup]
2026-10-31T20:17:11.4982348Z ##[group]Disabling automatic garbage collection
2026-10-31T20:17:11.4985649Z [command]/usr/bin/git config --local gc.auto 0
2026-10-31T20:17:11.5025306Z ##[endgroup]
2026-10-31T20:17:11.5027360Z ##[group]Setting up auth
2026-10-31T20:17:11.5032965Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-10-31T20:17:11.5075824Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-10-31T20:17:11.5606101Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-10-31T20:17:11.5656707Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-10-31T20:17:11.5931191Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-10-31T20:17:11.5968404Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-10-31T20:17:11.6245052Z [command]/usr/bin/git config --local http.https://github.com/.extraheader AUTHORIZATION: basic ***
2026-10-31T20:17:11.6285208Z ##[endgroup]
2026-10-31T20:17:11.6286974Z ##[group]Fetching the repository
2026-10-31T20:17:11.6297695Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +fb4c48ac36085426af207751a803572b780fcbd1:refs/remotes/pull/5/merge
2026-10-31T20:17:11.9340047Z From https://github.com/amitmanchella-cog/GxP-Documentation-Demo
2026-10-31T20:17:11.9341760Z  * [new ref]         fb4c48ac36085426af207751a803572b780fcbd1 -> pull/5/merge
2026-10-31T20:17:11.9347617Z ##[endgroup]
2026-10-31T20:17:11.9362919Z ##[group]Determining the checkout info
2026-10-31T20:17:11.9364626Z ##[endgroup]
2026-10-31T20:17:11.9365527Z [command]/usr/bin/git sparse-checkout disable
2026-10-31T20:17:11.9427525Z [command]/usr/bin/git config --local --unset-all extensions.worktreeConfig
2026-10-31T20:17:11.9468612Z ##[group]Checking out the ref
2026-10-31T20:17:11.9471608Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/5/merge
2026-10-31T20:17:11.9562997Z Note: switching to 'refs/remotes/pull/5/merge'.
2026-10-31T20:17:11.9564491Z 
2026-10-31T20:17:11.9565323Z You are in 'detached HEAD' state. You can look around, make experimental
2026-10-31T20:17:11.9566841Z changes and commit them, and you can discard any commits you make in this
2026-10-31T20:17:11.9568036Z state without impacting any branches by switching back to a branch.
2026-10-31T20:17:11.9569071Z 
2026-10-31T20:17:11.9569604Z If you want to create a new branch to retain commits you create, you may
2026-10-31T20:17:11.9570723Z do so (now or later) by using -c with the switch command. Example:
2026-10-31T20:17:11.9571393Z 
2026-10-31T20:17:11.9571718Z   git switch -c <new-branch-name>
2026-10-31T20:17:11.9572195Z 
2026-10-31T20:17:11.9572513Z Or undo this operation with:
2026-10-31T20:17:11.9572939Z 
2026-10-31T20:17:11.9573229Z   git switch -
2026-10-31T20:17:11.9573545Z 
2026-10-31T20:17:11.9581815Z Turn off this advice by setting config variable advice.detachedHead to false
2026-10-31T20:17:11.9582799Z 
2026-10-31T20:17:11.9584338Z HEAD is now at fb4c48a Merge 43da149adc9cb2738bf7905dfd2fa3b98ac88533 into f28a790c3ad768d5227c3726eb45b57daa158815
2026-10-31T20:17:11.9587198Z ##[endgroup]
2026-10-31T20:17:11.9623637Z [command]/usr/bin/git log -1 --format=%H
2026-10-31T20:17:11.9730044Z fb4c48ac36085426af207751a803572b780fcbd1
2026-10-31T20:17:12.0018030Z ##[group]Run actions/setup-python@v5
2026-10-31T20:17:12.0018869Z with:
2026-10-31T20:17:12.0019397Z   python-version: 3.12
2026-10-31T20:17:12.0020034Z   check-latest: false
2026-10-31T20:17:12.0030221Z   token: ***
2026-10-31T20:17:12.0030786Z   update-environment: true
2026-10-31T20:17:12.0031512Z   allow-prereleases: false
2026-10-31T20:17:12.0032201Z   freethreaded: false
2026-10-31T20:17:12.0032798Z ##[endgroup]
2026-10-31T20:17:12.1455317Z ##[group]Installed versions
2026-10-31T20:17:12.1588258Z (node:2349) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-10-31T20:17:12.1592350Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-10-31T20:17:12.1594998Z Successfully set up CPython (3.12.15)
2026-10-31T20:17:12.1597009Z ##[endgroup]
2026-10-31T20:17:12.1809236Z ##[group]Run pip install -e ".[dev]"
2026-10-31T20:17:12.1810669Z [36;1mpip install -e ".[dev]"[0m
2026-10-31T20:17:12.1886727Z shell: /usr/bin/bash -e {0}
2026-10-31T20:17:12.1887862Z env:
2026-10-31T20:17:12.1889005Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:12.1891355Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib/pkgconfig
2026-10-31T20:17:12.1893734Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:12.1896013Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:12.1898102Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:12.1900262Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib
2026-10-31T20:17:12.1901969Z ##[endgroup]
2026-10-31T20:17:12.9207456Z Obtaining file:///home/runner/work/GxP-Documentation-Demo/GxP-Documentation-Demo
2026-10-31T20:17:12.9223305Z   Installing build dependencies: started
2026-10-31T20:17:13.6707820Z   Installing build dependencies: finished with status 'done'
2026-10-31T20:17:13.6716736Z   Checking if build backend supports build_editable: started
2026-10-31T20:17:14.0581099Z   Checking if build backend supports build_editable: finished with status 'done'
2026-10-31T20:17:14.0592194Z   Getting requirements to build editable: started
2026-10-31T20:17:14.4016735Z   Getting requirements to build editable: finished with status 'done'
2026-10-31T20:17:14.4025053Z   Preparing editable metadata (pyproject.toml): started
2026-10-31T20:17:14.6022183Z   Preparing editable metadata (pyproject.toml): finished with status 'done'
2026-10-31T20:17:14.6739304Z Collecting fastapi<0.116,>=0.110 (from sst==3.4.1)
2026-10-31T20:17:14.6949090Z   Downloading fastapi-0.115.14-py3-none-any.whl.metadata (27 kB)
2026-10-31T20:17:14.7215076Z Collecting uvicorn>=0.29 (from uvicorn[standard]>=0.29->sst==3.4.1)
2026-10-31T20:17:14.7250741Z   Downloading uvicorn-0.54.0-py3-none-any.whl.metadata (6.6 kB)
2026-10-31T20:17:14.7394920Z Collecting jinja2>=3.1 (from sst==3.4.1)
2026-10-31T20:17:14.7500760Z   Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
2026-10-31T20:17:14.7844212Z Collecting pyyaml>=6 (from sst==3.4.1)
2026-10-31T20:17:14.7874212Z   Downloading pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.4 kB)
2026-10-31T20:17:14.8002180Z Collecting python-multipart>=0.0.9 (from sst==3.4.1)
2026-10-31T20:17:14.8032975Z   Downloading python_multipart-0.0.33-py3-none-any.whl.metadata (6.3 kB)
2026-10-31T20:17:14.8379244Z Collecting pytest>=8 (from sst==3.4.1)
2026-10-31T20:17:14.8410129Z   Downloading pytest-9.2.0-py3-none-any.whl.metadata (7.9 kB)
2026-10-31T20:17:14.8584748Z Collecting pytest-cov>=5 (from sst==3.4.1)
2026-10-31T20:17:14.8614526Z   Downloading pytest_cov-7.1.0-py3-none-any.whl.metadata (32 kB)
2026-10-31T20:17:14.8783424Z Collecting httpx>=0.27 (from sst==3.4.1)
2026-10-31T20:17:14.8814469Z   Downloading httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
2026-10-31T20:17:15.2064768Z Collecting ruff>=0.5 (from sst==3.4.1)
2026-10-31T20:17:15.2098326Z   Downloading ruff-0.17.3-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (20 kB)
2026-10-31T20:17:15.2335085Z Collecting starlette<0.47.0,>=0.40.0 (from fastapi<0.116,>=0.110->sst==3.4.1)
2026-10-31T20:17:15.2364751Z   Downloading starlette-0.46.2-py3-none-any.whl.metadata (6.2 kB)
2026-10-31T20:17:15.3368422Z Collecting pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4 (from fastapi<0.116,>=0.110->sst==3.4.1)
2026-10-31T20:17:15.3400941Z   Downloading pydantic-2.14.2-py3-none-any.whl.metadata (137 kB)
2026-10-31T20:17:15.3611522Z Collecting typing-extensions>=4.8.0 (from fastapi<0.116,>=0.110->sst==3.4.1)
2026-10-31T20:17:15.3644292Z   Downloading typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
2026-10-31T20:17:15.3759398Z Collecting annotated-types>=0.6.0 (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4->fastapi<0.116,>=0.110->sst==3.4.1)
2026-10-31T20:17:15.3791309Z   Downloading annotated_types-0.8.0-py3-none-any.whl.metadata (15 kB)
2026-10-31T20:17:16.0434338Z Collecting pydantic-core==2.50.2 (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4->fastapi<0.116,>=0.110->sst==3.4.1)
2026-10-31T20:17:16.0466752Z   Downloading pydantic_core-2.50.2-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (6.5 kB)
2026-10-31T20:17:16.0576958Z Collecting typing-inspection>=0.4.4 (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4->fastapi<0.116,>=0.110->sst==3.4.1)
2026-10-31T20:17:16.0605348Z   Downloading typing_inspection-0.4.4-py3-none-any.whl.metadata (2.6 kB)
2026-10-31T20:17:16.0800249Z Collecting anyio<5,>=3.6.2 (from starlette<0.47.0,>=0.40.0->fastapi<0.116,>=0.110->sst==3.4.1)
2026-10-31T20:17:16.0830664Z   Downloading anyio-4.15.1-py3-none-any.whl.metadata (4.7 kB)
2026-10-31T20:17:16.0971736Z Collecting idna>=2.8 (from anyio<5,>=3.6.2->starlette<0.47.0,>=0.40.0->fastapi<0.116,>=0.110->sst==3.4.1)
2026-10-31T20:17:16.1001747Z   Downloading idna-3.20-py3-none-any.whl.metadata (7.2 kB)
2026-10-31T20:17:16.1219091Z Collecting certifi (from httpx>=0.27->sst==3.4.1)
2026-10-31T20:17:16.1250386Z   Downloading certifi-2026.10.23-py3-none-any.whl.metadata (2.5 kB)
2026-10-31T20:17:16.1399308Z Collecting httpcore==1.* (from httpx>=0.27->sst==3.4.1)
2026-10-31T20:17:16.1430707Z   Downloading httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
2026-10-31T20:17:16.1552265Z Collecting h11>=0.16 (from httpcore==1.*->httpx>=0.27->sst==3.4.1)
2026-10-31T20:17:16.1582016Z   Downloading h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
2026-10-31T20:17:16.2121931Z Collecting MarkupSafe>=2.0 (from jinja2>=3.1->sst==3.4.1)
2026-10-31T20:17:16.2154172Z   Downloading markupsafe-3.0.4-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
2026-10-31T20:17:16.2263484Z Collecting iniconfig>=2 (from pytest>=8->sst==3.4.1)
2026-10-31T20:17:16.2293140Z   Downloading iniconfig-2.3.1-py3-none-any.whl.metadata (2.8 kB)
2026-10-31T20:17:16.2439651Z Collecting packaging>=24 (from pytest>=8->sst==3.4.1)
2026-10-31T20:17:16.2606172Z   Downloading packaging-26.3-py3-none-any.whl.metadata (3.5 kB)
2026-10-31T20:17:16.2727470Z Collecting pluggy<2,>=1.6 (from pytest>=8->sst==3.4.1)
2026-10-31T20:17:16.2756879Z   Downloading pluggy-1.7.0-py3-none-any.whl.metadata (5.0 kB)
2026-10-31T20:17:16.2917209Z Collecting pygments>=2.15 (from pytest>=8->sst==3.4.1)
2026-10-31T20:17:16.2947182Z   Downloading pygments-2.21.0-py3-none-any.whl.metadata (2.5 kB)
2026-10-31T20:17:16.7120244Z Collecting coverage>=7.10.6 (from coverage[toml]>=7.10.6->pytest-cov>=5->sst==3.4.1)
2026-10-31T20:17:16.7154433Z   Downloading coverage-7.17.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (8.1 kB)
2026-10-31T20:17:16.7414342Z Collecting click>=7.0 (from uvicorn>=0.29->uvicorn[standard]>=0.29->sst==3.4.1)
2026-10-31T20:17:16.7446580Z   Downloading click-8.5.0-py3-none-any.whl.metadata (2.6 kB)
2026-10-31T20:17:16.7833783Z Collecting httptools>=0.8.0 (from uvicorn[standard]>=0.29->sst==3.4.1)
2026-10-31T20:17:16.7867711Z   Downloading httptools-0.9.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (3.5 kB)
2026-10-31T20:17:16.8017300Z Collecting python-dotenv>=0.13 (from uvicorn[standard]>=0.29->sst==3.4.1)
2026-10-31T20:17:16.8051001Z   Downloading python_dotenv-1.2.4-py3-none-any.whl.metadata (29 kB)
2026-10-31T20:17:16.8447121Z Collecting uvloop>=0.15.1 (from uvicorn[standard]>=0.29->sst==3.4.1)
2026-10-31T20:17:16.8480702Z   Downloading uvloop-0.23.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (5.1 kB)
2026-10-31T20:17:16.9220105Z Collecting watchfiles>=0.20 (from uvicorn[standard]>=0.29->sst==3.4.1)
2026-10-31T20:17:16.9255006Z   Downloading watchfiles-1.3.0-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.9 kB)
2026-10-31T20:17:17.0476674Z Collecting websockets>=13.0 (from uvicorn[standard]>=0.29->sst==3.4.1)
2026-10-31T20:17:17.0511383Z   Downloading websockets-17.4-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (6.3 kB)
2026-10-31T20:17:17.0633091Z Downloading fastapi-0.115.14-py3-none-any.whl (95 kB)
2026-10-31T20:17:17.0693600Z Downloading pydantic-2.14.2-py3-none-any.whl (490 kB)
2026-10-31T20:17:17.0767263Z Downloading pydantic_core-2.50.2-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (2.2 MB)
2026-10-31T20:17:17.0874604Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.2/2.2 MB 250.0 MB/s  0:00:00
2026-10-31T20:17:17.0907390Z Downloading starlette-0.46.2-py3-none-any.whl (72 kB)
2026-10-31T20:17:17.0961607Z Downloading anyio-4.15.1-py3-none-any.whl (132 kB)
2026-10-31T20:17:17.1012734Z Downloading annotated_types-0.8.0-py3-none-any.whl (13 kB)
2026-10-31T20:17:17.1060315Z Downloading httpx-0.28.1-py3-none-any.whl (73 kB)
2026-10-31T20:17:17.1109239Z Downloading httpcore-1.0.9-py3-none-any.whl (78 kB)
2026-10-31T20:17:17.1160558Z Downloading h11-0.16.0-py3-none-any.whl (37 kB)
2026-10-31T20:17:17.1207737Z Downloading idna-3.20-py3-none-any.whl (69 kB)
2026-10-31T20:17:17.1257987Z Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
2026-10-31T20:17:17.1310129Z Downloading markupsafe-3.0.4-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
2026-10-31T20:17:17.1357571Z Downloading pytest-9.2.0-py3-none-any.whl (411 kB)
2026-10-31T20:17:17.1414687Z Downloading pluggy-1.7.0-py3-none-any.whl (27 kB)
2026-10-31T20:17:17.1461964Z Downloading iniconfig-2.3.1-py3-none-any.whl (7.6 kB)
2026-10-31T20:17:17.1508843Z Downloading packaging-26.3-py3-none-any.whl (129 kB)
2026-10-31T20:17:17.1559969Z Downloading pygments-2.21.0-py3-none-any.whl (1.3 MB)
2026-10-31T20:17:17.1629270Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 211.1 MB/s  0:00:00
2026-10-31T20:17:17.1659909Z Downloading pytest_cov-7.1.0-py3-none-any.whl (22 kB)
2026-10-31T20:17:17.1709255Z Downloading coverage-7.17.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (261 kB)
2026-10-31T20:17:17.1790578Z Downloading python_multipart-0.0.33-py3-none-any.whl (32 kB)
2026-10-31T20:17:17.1842009Z Downloading pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (807 kB)
2026-10-31T20:17:17.1900488Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 807.9/807.9 kB 148.0 MB/s  0:00:00
2026-10-31T20:17:17.1931308Z Downloading ruff-0.17.3-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (10.6 MB)
2026-10-31T20:17:17.2247033Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.6/10.6 MB 354.2 MB/s  0:00:00
2026-10-31T20:17:17.2281070Z Downloading typing_extensions-4.16.0-py3-none-any.whl (45 kB)
2026-10-31T20:17:17.2332180Z Downloading typing_inspection-0.4.4-py3-none-any.whl (14 kB)
2026-10-31T20:17:17.2380839Z Downloading uvicorn-0.54.0-py3-none-any.whl (87 kB)
2026-10-31T20:17:17.2430173Z Downloading click-8.5.0-py3-none-any.whl (125 kB)
2026-10-31T20:17:17.2522025Z Downloading httptools-0.9.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (552 kB)
2026-10-31T20:17:17.2814688Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 552.8/552.8 kB 113.0 MB/s  0:00:00
2026-10-31T20:17:17.2846749Z Downloading python_dotenv-1.2.4-py3-none-any.whl (23 kB)
2026-10-31T20:17:17.2897635Z Downloading uvloop-0.23.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (4.5 MB)
2026-10-31T20:17:17.3040005Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.5/4.5 MB 353.7 MB/s  0:00:00
2026-10-31T20:17:17.3070467Z Downloading watchfiles-1.3.0-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (458 kB)
2026-10-31T20:17:17.3131358Z Downloading websockets-17.4-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (226 kB)
2026-10-31T20:17:17.3182479Z Downloading certifi-2026.10.23-py3-none-any.whl (135 kB)
2026-10-31T20:17:17.4145606Z Building wheels for collected packages: sst
2026-10-31T20:17:17.4153301Z   Building editable for sst (pyproject.toml): started
2026-10-31T20:17:17.6286046Z   Building editable for sst (pyproject.toml): finished with status 'done'
2026-10-31T20:17:17.6292300Z   Created wheel for sst: filename=sst-3.4.1-0.editable-py3-none-any.whl size=2741 sha256=4f92727feaaa797980a3bb27c02968845625a3f9e311eda1b5d356d08add235d
2026-10-31T20:17:17.6295384Z   Stored in directory: /tmp/pip-ephem-wheel-cache-x5i5rf8f/wheels/c0/6e/90/8bf674a4002fac32e3f1bf89eccca0d6a85d08d7a749515856
2026-10-31T20:17:17.6309375Z Successfully built sst
2026-10-31T20:17:17.6928422Z Installing collected packages: websockets, uvloop, typing-extensions, ruff, pyyaml, python-multipart, python-dotenv, pygments, pluggy, packaging, MarkupSafe, iniconfig, idna, httptools, h11, coverage, click, certifi, annotated-types, uvicorn, typing-inspection, pytest, pydantic-core, jinja2, httpcore, anyio, watchfiles, starlette, pytest-cov, pydantic, httpx, fastapi, sst
2026-10-31T20:17:20.4911696Z 
2026-10-31T20:17:20.4945495Z Successfully installed MarkupSafe-3.0.4 annotated-types-0.8.0 anyio-4.15.1 certifi-2026.10.23 click-8.5.0 coverage-7.17.0 fastapi-0.115.14 h11-0.16.0 httpcore-1.0.9 httptools-0.9.0 httpx-0.28.1 idna-3.20 iniconfig-2.3.1 jinja2-3.1.6 packaging-26.3 pluggy-1.7.0 pydantic-2.14.2 pydantic-core-2.50.2 pygments-2.21.0 pytest-9.2.0 pytest-cov-7.1.0 python-dotenv-1.2.4 python-multipart-0.0.33 pyyaml-6.0.3 ruff-0.17.3 sst-3.4.1 starlette-0.46.2 typing-extensions-4.16.0 typing-inspection-0.4.4 uvicorn-0.54.0 uvloop-0.23.0 watchfiles-1.3.0 websockets-17.4
2026-10-31T20:17:20.6223387Z ##[group]Run ruff check .
2026-10-31T20:17:20.6223694Z [36;1mruff check .[0m
2026-10-31T20:17:20.6255681Z shell: /usr/bin/bash -e {0}
2026-10-31T20:17:20.6255936Z env:
2026-10-31T20:17:20.6256214Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6256671Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib/pkgconfig
2026-10-31T20:17:20.6257108Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6257496Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6257881Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6258270Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib
2026-10-31T20:17:20.6258767Z ##[endgroup]
2026-10-31T20:17:20.6408176Z All checks passed!
2026-10-31T20:17:20.6452859Z ##[group]Run ruff format --check .
2026-10-31T20:17:20.6453175Z [36;1mruff format --check .[0m
2026-10-31T20:17:20.6483439Z shell: /usr/bin/bash -e {0}
2026-10-31T20:17:20.6483692Z env:
2026-10-31T20:17:20.6484206Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6484670Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib/pkgconfig
2026-10-31T20:17:20.6485107Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6485503Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6485891Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6486302Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib
2026-10-31T20:17:20.6486629Z ##[endgroup]
2026-10-31T20:17:20.6628227Z 40 files already formatted
2026-10-31T20:17:20.6672873Z ##[group]Run mkdir -p reports && set -o pipefail && pytest --junitxml=reports/junit.xml --cov-report=xml:reports/coverage.xml | tee reports/pytest.txt
2026-10-31T20:17:20.6674324Z [36;1mmkdir -p reports && set -o pipefail && pytest --junitxml=reports/junit.xml --cov-report=xml:reports/coverage.xml | tee reports/pytest.txt[0m
2026-10-31T20:17:20.6703739Z shell: /usr/bin/bash -e {0}
2026-10-31T20:17:20.6704252Z env:
2026-10-31T20:17:20.6704556Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6705040Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib/pkgconfig
2026-10-31T20:17:20.6705481Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6705875Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6706259Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:20.6706652Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib
2026-10-31T20:17:20.6707013Z ##[endgroup]
2026-10-31T20:17:24.8251449Z ..............................................................           [100%]
2026-10-31T20:17:24.8252245Z =============================== warnings summary ===============================
2026-10-31T20:17:24.8253238Z ../../../../../opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/site-packages/starlette/testclient.py:37
2026-10-31T20:17:24.8255241Z   /opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/site-packages/starlette/testclient.py:37: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
2026-10-31T20:17:24.8256837Z     _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]
2026-10-31T20:17:24.8257397Z 
2026-10-31T20:17:24.8257705Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-10-31T20:17:24.8258349Z ================================ tests coverage ================================
2026-10-31T20:17:24.8258991Z _______________ coverage: platform linux, python 3.12.15-final-0 _______________
2026-10-31T20:17:24.8259419Z 
2026-10-31T20:17:24.8259578Z Name              Stmts   Miss  Cover   Missing
2026-10-31T20:17:24.8260004Z -----------------------------------------------
2026-10-31T20:17:24.8260408Z sst/__init__.py       1      0   100%
2026-10-31T20:17:24.8260786Z sst/audit.py         16      1    94%   34
2026-10-31T20:17:24.8261211Z sst/db.py            33     10    70%   58-59, 63-69, 84
2026-10-31T20:17:24.8261693Z sst/main.py         232      6    97%   43-45, 53, 248, 501
2026-10-31T20:17:24.8262134Z sst/regimes.py       42      0   100%
2026-10-31T20:17:24.8262504Z sst/rounding.py      23      0   100%
2026-10-31T20:17:24.8262949Z sst/seed.py         104     12    88%   165, 211, 236, 242, 295-301, 305
2026-10-31T20:17:24.8263450Z -----------------------------------------------
2026-10-31T20:17:24.8263785Z TOTAL               451     29    94%
2026-10-31T20:17:24.8264360Z Coverage XML written to file reports/coverage.xml
2026-10-31T20:17:24.8264762Z Required test coverage of 85% reached. Total coverage: 93.57%
2026-10-31T20:17:24.8265450Z 62 passed, 1 warning in 2.56s
2026-10-31T20:17:24.9177154Z ##[group]Run actions/upload-artifact@v4
2026-10-31T20:17:24.9177469Z with:
2026-10-31T20:17:24.9177667Z   name: test-evidence
2026-10-31T20:17:24.9177892Z   path: reports/
2026-10-31T20:17:24.9178106Z   if-no-files-found: warn
2026-10-31T20:17:24.9178341Z   compression-level: 6
2026-10-31T20:17:24.9178551Z   overwrite: false
2026-10-31T20:17:24.9178760Z   include-hidden-files: false
2026-10-31T20:17:24.9178994Z env:
2026-10-31T20:17:24.9179243Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:24.9179679Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib/pkgconfig
2026-10-31T20:17:24.9180107Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:24.9180490Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:24.9180906Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.15/x64
2026-10-31T20:17:24.9181311Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.15/x64/lib
2026-10-31T20:17:24.9181660Z ##[endgroup]
2026-10-31T20:17:25.0947526Z (node:2562) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-10-31T20:17:25.0948647Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-10-31T20:17:25.1055270Z With the provided path, there will be 3 files uploaded
2026-10-31T20:17:25.1056121Z Artifact name is valid!
2026-10-31T20:17:25.1056375Z Root directory input is valid!
2026-10-31T20:17:25.3301918Z Beginning upload of artifact content to blob storage
2026-10-31T20:17:25.3672292Z (node:2562) [DEP0169] DeprecationWarning: `url.parse()` behavior is not standardized and prone to errors that have security implications. Use the WHATWG URL API instead. CVEs are not issued for `url.parse()` vulnerabilities.
2026-10-31T20:17:25.4600049Z Uploaded bytes 3875
2026-10-31T20:17:25.4907479Z Finished uploading artifact content to blob storage!
2026-10-31T20:17:25.4909114Z SHA256 digest of uploaded artifact zip is d70b4a04945533ed2d5c3d8c0b154beb3e4d300c1865734d23cd549663038941
2026-10-31T20:17:25.4910532Z Finalizing artifact upload
2026-10-31T20:17:25.9161061Z Artifact test-evidence.zip successfully finalized. Artifact ID 13056254013
2026-10-31T20:17:25.9162164Z Artifact test-evidence has been successfully uploaded! Final size is 3875 bytes. Artifact ID is 13056254013
2026-10-31T20:17:25.9169808Z Artifact download URL: https://github.com/amitmanchella-cog/GxP-Documentation-Demo/actions/runs/41238179614/artifacts/13056254013
2026-10-31T20:17:25.9367755Z Post job cleanup.
2026-10-31T20:17:26.0612060Z (node:2576) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-10-31T20:17:26.0613125Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-10-31T20:17:26.0798261Z Post job cleanup.
2026-10-31T20:17:26.1864924Z [command]/usr/bin/git version
2026-10-31T20:17:26.1950889Z git version 2.56.0
2026-10-31T20:17:26.1999357Z Temporarily overriding HOME='/home/runner/work/_temp/6161ad3e-f2fd-4d65-9a45-f29d9a3af446' before making global git config changes
2026-10-31T20:17:26.2002939Z Adding repository directory to the temporary git global config as a safe directory
2026-10-31T20:17:26.2007462Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/GxP-Documentation-Demo/GxP-Documentation-Demo
2026-10-31T20:17:26.2075546Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-10-31T20:17:26.2136194Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-10-31T20:17:26.2570408Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-10-31T20:17:26.2626899Z http.https://github.com/.extraheader
2026-10-31T20:17:26.2648673Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-10-31T20:17:26.2715994Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-10-31T20:17:26.3030020Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-10-31T20:17:26.3072085Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-10-31T20:17:26.3531649Z Cleaning up orphan processes
2026-10-31T20:17:26.4123066Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4, actions/setup-python@v5, actions/upload-artifact@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/

```

## Attached artefacts
CI artifact `test-evidence` (Artifact ID 13056254013): `reports/junit.xml`, `reports/coverage.xml` — https://github.com/amitmanchella-cog/GxP-Documentation-Demo/actions/runs/41238179614/artifacts/13056254013

Regression proof (local, informative only, not CI evidence): `PRE-FIX-CHG-4127-TS-005.md`, `PRE-FIX-CHG-4127-TS-006.md`.
