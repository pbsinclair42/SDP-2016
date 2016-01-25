
To push your code use this sequence :
git pull
git add .
git commit -m "What I have done is..."
git push



git reset origin/master -- file
If you have over written a file, say this.txt, use this.

git add -i` 
which lets you select which changes to a file you want to stage for commit, rather than the whole file. i is for interactive

People will like you if you pull before you start to work.

git status
is super useful. It lets you know which files you've added/modified/removed/staged ... 

_________________________
Branching

Woah, such advanced.

git checkout -b {branch_name} {base_branch}   
The base_branch if not supplied is the one you are currently on.
will create a new branch called {branch_name} which contains everything in base_branch 

git checkout {branch_name} 
will move you to the other branch

git branch --all 
To see every branch - even the remote ones!

git branch -d    
To delete the current branch

git pull --rebase origin master 
Will update your branch with the master changes. you will probably get some conflicts. git is really helpful, it tells you what you need to do to resolve them
Basically: 
git status              // to get the file names that need to be merged
vim <some-file>         // open the text editor to remove the conflicts. see the --theirs / --ours checkout below.
git add <some-file>      
git rebase --continue
# repeat

git checkout [--theirs | --ours ] <file name>
When there are merge conflicts, you can use this to just take the other version or pick yours!

git push origin --delete {branch_name} 
To remove a remote branch.

_________________________
also investigate:
git fetch
git revert 
