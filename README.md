# .github

Org-wide files for Ghost-Crafters.

| Path | What it does |
|---|---|
| [`profile/README.md`](profile/README.md) | The org page at [github.com/Ghost-Crafters](https://github.com/Ghost-Crafters) |
| [`SECURITY.md`](SECURITY.md) | Security policy for every repo that doesn't have its own |
| [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE) | Bug report and feature request forms, plus the New issue page links, for every repo without its own templates |
| [`labels.json`](labels.json) | The label set the repos use |
| [`.github/workflows/claude-review.yml`](.github/workflows/claude-review.yml) | Claude reviews every pull request on the strongest Claude model and grades each finding P0 to P3. The check fails on any P0 or P1, and its summary names the commit it reviewed. Other repos call it as a reusable workflow |
| [`.github/workflows/claude.yml`](.github/workflows/claude.yml) | Claude answers when someone with write access mentions @claude in an issue or pull request |
| [`tools/check_forms.py`](tools/check_forms.py) | Checks the issue forms. The [Forms workflow](.github/workflows/forms.yml) runs it on every pull request |

The security policy and the issue forms apply to every repo in the org that has none of its own ([how GitHub picks them up](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)), so a change here shows up everywhere at once. Changes go through a pull request like in any other repo.

Run the form check locally with:

```sh
python3 tools/check_forms.py
python3 -m unittest discover -s tools
```
