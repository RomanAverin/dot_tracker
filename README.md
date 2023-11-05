# dot_tracker
**In development, soon to be available**

The utility is designed for easy management of operating system and application configuration files.

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
and create folder for tracked dot files
`mkdir ~/.dotfiles`

After that you may track configuration, examle config of zsh:

`dot_tracker add zsh -n zsh -files ~/.zshrc`

