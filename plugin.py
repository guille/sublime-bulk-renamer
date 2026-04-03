import pathlib

import sublime
import sublime_plugin

from .internal.order_renames import order_rename_graph


class SbrBulkRenameInDirCommand(sublime_plugin.WindowCommand):
    def run(self, dirs: "list[str] | None" = None):
        expanded_dirs: "list[str] | None" = sublime.expand_variables(  # pyright: ignore[reportAssignmentType]
            dirs, sublime.active_window().extract_variables()
        )
        if expanded_dirs is None:
            expanded_dirs = []

        if len(expanded_dirs) != 1:
            return self.window.status_message(
                f"Expected one dir only, got {len(expanded_dirs)}"
            )

        path = pathlib.Path(expanded_dirs[0])
        if not path.is_absolute():
            return self.window.status_message(f"Expected absolute path, got {path}")
        if not path.exists():
            return self.window.status_message(f"Couldn't find {path}")
        if not path.is_dir():
            return self.window.status_message(f"Expected {path} to be a directory")

        initial = sorted([str(p.relative_to(path)) for p in path.iterdir()])
        template = self._generate_template(path, initial)

        view = self.window.new_file()
        view.set_name(f"Bulk rename ({path.name})")
        view.set_scratch(True)
        view.settings().set("is_sbr_buffer", True)
        view.settings().set("sbr_path", str(path))
        view.settings().set("sbr_initial_dirs", initial)
        view.run_command("sbr_insert_content", {"text": template})

    def _generate_template(self, path: pathlib.Path, children: "list[str]") -> str:
        header = (
            f"# each line below corresponds to an entry in the directory {path}\n"
            "# the entries are identified by the position, so moving lines equals swapping names\n"
            "# empty lines or those starting with # are ignored\n"
            "# close the tab once you're done renaming\n\n"
        )
        return header + "\n".join(children) + "\n"

    def is_visible(self, dirs: "list[str] | None" = None) -> bool:
        return (dirs is not None) and (len(dirs) == 1)


class SbrInsertContentCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, text: str = ""):
        self.view.insert(edit, 0, text)


class SbrClosedEventListener(sublime_plugin.ViewEventListener):
    def on_pre_close(self):
        window = self.view.window()
        if window is None:
            return

        root_path = self.view.settings().get("sbr_path")
        if root_path is None or not isinstance(root_path, str):
            return window.status_message(f"Can't parse sbr_path: {root_path}")
        root_path = pathlib.Path(root_path)

        initial_dirs = self.view.settings().get("sbr_initial_dirs")
        if initial_dirs is None or not isinstance(initial_dirs, list):
            return window.status_message(
                f"Can't parse sbr_initial_dirs: {initial_dirs}"
            )

        lines = self.view.lines(sublime.Region(0, self.view.size()))
        final_dirs: list[str] = []
        for line in lines:
            line_text = self.view.substr(line)
            # Skip empty lines or comments
            if line_text.startswith("#") or not line_text:
                continue

            final_dirs.append(line_text)

        if len(initial_dirs) != len(final_dirs):
            return window.status_message(
                f"Mismatch in dir sizes: initial count was {len(initial_dirs)} and new count is {len(final_dirs)}"
            )

        if len(final_dirs) != len(set(final_dirs)):
            return window.status_message(
                "Ambiguous operation detected: can't rename multiple elements to the same location"
            )

        result = order_rename_graph(list(zip(initial_dirs, final_dirs)))
        for src, dst in result:
            print(f"Renaming {src} -> {dst}")
            src = root_path / pathlib.Path(src)
            dst = root_path / pathlib.Path(dst)
            src.rename(dst)

    @classmethod
    def is_applicable(cls, settings: sublime.Settings) -> bool:
        return settings.get("is_sbr_buffer", False) is True
