## Contribution Guide
**Please Read this Section Before Contributing**

if you gonna edit any part of code, create new branch for it, with this pattern:

```
S{sprint number}_NameForBranch
```
for example `S1_AddingNewFutureToUser` which is a new branch in sprint 1.

for creating new branch from `master` branch, you can use this command as example. in root directory of project:

```git
git checkout -b S1_NewBranchName master
```

if you commit code related to an issue, provide the issue number in this format:
```
this is the commit message of fixing X issue [TTHREE-102]
```
the `TTHREE-` is what issues are started with in [Jira](http://jira.rahnemacollege.com) for team 3, so follow this rule.

also you can use this tags in comments to make code much more readable too.
also if you use PyCharm you can find these tags by navigating to **`TODO`** panel in bottom:

`todo` could be used to mark something that should be done in future.

`fixme` could be used to notify a problem that must be fixed later.

`snippet` could be used for commented lines of code, that you want to keep them as snippet.

also we use [Semantic Versioning](https://semver.org/), if you don't know how it works, follow the link.
