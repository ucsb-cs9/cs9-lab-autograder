# cs9-lab-autograder
CS9 autograder development repo

## Setting up this autograder

### Upgrading an older autograder to use this library

Clone this library into the new autograder's directory.
The following command will add this repository as a git submodule.

```sh
# run inside the autograder's directory:
git submodule add git@github.com:ucsb-cs9/cs9-lab-autograder.git
```

Add the relative directory to `requirements.txt`:

```txt
-e ./cs9-lab-autograder
```
