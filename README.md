# .github

Org-wide files for Ghost-Crafters.

| Path | What it does |
|---|---|
| `profile/README.md` | The org page at github.com/Ghost-Crafters |
| `SECURITY.md` | Security policy for every repo that doesn't have its own |
| `.github/ISSUE_TEMPLATE/` | Bug report and feature request forms, plus the New issue page links, for every repo without its own templates |
| `labels.json` | The label set the repos use |
| `tools/check_forms.py` | Checks the issue forms; CI runs it on every pull request |

The security policy and the issue forms apply to every repo in the org that has none of its own, so a change here shows up everywhere at once. Changes go through a pull request like in any other repo.

Run the form check locally with:

```sh
python3 tools/check_forms.py
python3 -m unittest discover -s tools
```
