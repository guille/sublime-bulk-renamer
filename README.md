# Sublime Bulk Renamer

Sublime Bulk Renamer (sbr) allows you to bring the power of Sublime Text to... rename files in a directory.

Heavily inspired by [oil.nvim](https://github.com/stevearc/oil.nvim) and [nnn](https://github.com/jarun/nnn/)'s batch renamer. If you haven't used those, a video is perhaps the best way to introduce it:

https://github.com/user-attachments/assets/d457768d-2ce0-40ad-8a40-f22da839e094

## Features

- You can do basically anything that Sublime and Python's Pathlib support.
- Handles cycles and chains gracefully, so you can swap the name of two files without worrying about data loss or overridding them accidentally.
- This also allows you to quickly open Sublime Text to bulk rename the current directory from your terminal, for example (Linux/OSX):

```sh
subl --command 'sbr_bulk_rename_in_dir {"dirs": ["'"$(pwd)"'"]}'
```

## Limitations

- Unlike oil.nvim, this package does not allow creating or deleting files. This is intentionally not considered and is very unlikely to get added later on.
- Since sbr uses the `#` character for comments in the View that gets opened for renaming, the end state of a directory can't have any children whose name begin with `#`. Sorry! I might add escapes (`\#`) at some point if anyone really needs it.

## Future work

- add confirmation prompt on exit (settings-based)
- add visual indicators of file vs dir, maybe with annotation with the original name
- bulk rename including subdirectories, with configurable default depth
- (maybe) add side bar menu item for files, to bulk rename parent dir
