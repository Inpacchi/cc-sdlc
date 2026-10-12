# What the factory App does to agent text before posting it, for the report jobs (report.sh, and the
# comment bodies in factory-implement.yml, factory-plan.yml and factory-triage.yml):
#   jq -L .github/factory 'include "report"; .reason | clean'
# Tested in CI by tests/test_report.py.

# Agent text can't add markers (D1 rule 5).
def unmark: gsub("<!--"; "&lt;!--");

# Nor mention anyone or link an issue, which would notify or cross-reference. Triage's comment is only
# unmarked: it names related issues on purpose.
def clean: unmark | gsub("@(?=[A-Za-z0-9])"; "@​") | gsub("(?i)\\bGH-(?=[0-9])"; "GH​-")
  | gsub("/issues/(?=[0-9])"; "/issues/​") | gsub("#(?=[0-9])"; "#​");

# Never post anything token-shaped (D2 rule 3), or an image or embed (GitHub fetches them on view).
def credential_like: test("sk-ant-|gh[pousr]_[A-Za-z0-9_]|github_pat_|ctx7sk|-----BEGIN [A-Z ]*PRIVATE KEY-----");
def embed: test("!\\[|<\\s*(img|picture|source|video|audio|svg|iframe|object|embed)\\b"; "i");
