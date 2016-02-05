
To push your code use this sequence :
`git pull`
`git add .`
`git commit -m "What I have done is..."`
`git push`

`git rev-list --left-right --count master...test-branch`
Compare your test-branch with master. This will give output like "1   8" meaning that your branch is ahead of master by one commit and behind master by 8 commits.

`git reset origin/master -- file`
If you have over written a file, say this.txt, use this.

`git add -i`
which lets you select which changes to a file you want to stage for commit, rather than the whole file. i is for interactive
I think this is harder to get your head around than branching, and not usually useful day-to-day.

People will like you if you pull before you start to work.

`git status`
is super useful. It lets you know which files you've added/modified/removed/staged ... 

_________________________
Branching

Woah, such advanced.

`git checkout -b {branch_name} {base_branch}  ` 
The base_branch if not supplied is the one you are currently on.
will create a new branch called {branch_name} which contains everything in base_branch 

`git checkout {branch_name} `
will move you to the other branch

`git branch --all `
To see every branch - even the remote ones!

`git branch -d    `
To delete the current branch
You can use `git branch -d {branch_name}` to delete a specific branch.

`git pull --rebase origin master `
Will update your branch with the master changes. you will probably get some conflicts. git is really helpful, it tells you what you need to do to resolve them
Basically: 
`git status`              // to get the file names that need to be merged
`vim <some-file>`         // open the text editor to remove the conflicts. see the --theirs / --ours checkout below.
`git add <some-file>`      
`git rebase --continue`
then repeat

`git checkout [--theirs | --ours ] <file name>`
When there are merge conflicts, you can use this to just take the other version or pick yours!

`git checkout -- file`
undoes any unstaged changes to the file, useful if you basically want to undo a bunch of changes to a file.

`git checkout HEAD -- file`
undoes any staged or unstaged changes. So you have the same version as is on the server

`git reset --hard origin/{branch}`
hard resets your working tree to whatever is on origin.  Handy if you literally just want whatever's on the server for that branch.

`git push origin --delete {branch_name} `
To remove a remote branch.

`git fetch`
is like half of git pull - it checks to see if remote branches have changed but doesn't merge/rebase anything.  

`git revert`
tries to apply a 'reverse patch' of a commit, e.g. any line that was removed gets added, any line that was added gets removed

