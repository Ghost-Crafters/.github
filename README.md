# .github

Org-wide files for Ghost-Crafters.

| Path | What it does |
|---|---|
| [`profile/README.md`](profile/README.md) | The org page at [github.com/Ghost-Crafters](https://github.com/Ghost-Crafters) |
| [`SECURITY.md`](SECURITY.md) | Security policy for every repo that doesn't have its own |
| [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE) | Bug report and feature request forms, plus the New issue page links, for every repo without its own templates |
| [`labels.json`](labels.json) | The label set the repos use |
| [`tools/sync-labels.sh`](tools/sync-labels.sh) | Creates and updates the labels from `labels.json` in a repo |
| [`.github/workflows/stale-bug-reports.yml`](.github/workflows/stale-bug-reports.yml) | Reusable workflow that closes bug reports nobody answered |
| [`.github/workflows/edition-label.yml`](.github/workflows/edition-label.yml) | Reusable workflow that labels a bug report with its edition |
| [`tools/check_forms.py`](tools/check_forms.py) | Checks the issue forms. The [Forms workflow](.github/workflows/forms.yml) runs it on every pull request |

The security policy and the issue forms apply to every repo in the org that has none of its own ([how GitHub picks them up](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)), so a change here shows up everywhere at once. Changes go through a pull request like in any other repo.

Run the form check locally with:

```sh
python3 tools/check_forms.py
python3 -m unittest discover -s tools
```

## Syncing labels

```sh
tools/sync-labels.sh Ghost-Crafters/some-repo --dry-run
tools/sync-labels.sh Ghost-Crafters/some-repo
```

It needs the `gh` CLI signed in with access to the repo. Every group in `labels.json` is synced, and a second run changes nothing. Labels that aren't in the file are left alone. `--prune` deletes them, but never one that still has issues or pull requests on it. `--dry-run` prints each change and writes nothing. Per-repo labels such as `area:*` aren't in the file, so they are never touched without `--prune`.

## Stale bug reports

Public repos can call the reusable workflow to close bug reports that are waiting on the reporter. An issue labeled both `bug` and `waiting-for-reply` gets the `stale` label after 30 days without activity and is closed 14 days later. Any comment removes `stale` again, and `priority:high` issues are skipped. Pull requests and other issues are ignored. Add the `waiting-for-reply` label by hand when you ask the reporter a question.

```yaml
name: Stale bug reports
on:
  schedule:
    - cron: "17 4 * * *"
jobs:
  stale:
    permissions:
      actions: write
      issues: write
    uses: Ghost-Crafters/.github/.github/workflows/stale-bug-reports.yml@master
```

Run `tools/sync-labels.sh` in the repo first so both labels exist.

## Edition labels

The reusable edition workflow reads the Edition answer from a new bug report or feature request and adds `edition:bedrock` or `edition:java`. If the issue is edited and the answer changes, the old edition label comes off, and if the answer is removed both come off. Runs for one issue wait for each other and read the issue as it is now, so a late run can't bring back an old answer. The parser is [`tools/edition_label.py`](tools/edition_label.py). It reads the issue text from a file and only ever treats it as data.

```yaml
name: Edition label
on:
  issues:
    types: [opened, edited]
jobs:
  edition:
    permissions:
      issues: write
    uses: Ghost-Crafters/.github/.github/workflows/edition-label.yml@master
```
