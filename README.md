# dot_tracker
**In development, soon to be available**

_Only for Linux tested_

The utility is designed for easy management of operating system and application configuration files.

As a result of using the utility, you will have a directory with configurations and a description file inside(.dotfiles.yaml). You can then make it into a git repository and track changes. 

## Sample use

requirements:
  - python >= 3.10

`pip install dot_tracker`

Create example configuration file:
`touch ~/.dot_tracker.toml`

```
[general]
dotfiles = '~/.dotfiles'
repo_file = '~/.dotfiles/dotfiles.yaml'

```
or copy from repository.

and create folder for tracked dot files
`mkdir ~/.dotfiles`

After that you may track configuration, examle config of zsh:

`dot_tracker add zsh -n zsh -files ~/.zshrc`

The other commands can be found in help:

`dot_tracker -h`

