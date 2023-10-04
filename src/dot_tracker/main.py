import os
import uuid
import logging
import argparse
import pathlib
import tomllib
import shutil
import yaml

# import functools
# from typing import Callable


logging.basicConfig(level=logging.INFO)
FONT_RED = "\033[31m"
FONT_BOLD = "\033[1m"
FONT_RESET = "\033[0m"
log = logging.getLogger("main")


def load_config(file: str) -> dict | None:
    try:
        with open(file, "rb") as f:
            config = tomllib.load(f)
            return config
    except OSError as e:
        print(f"{FONT_BOLD}Error open exist configurations: {FONT_RED}{e}{FONT_RESET}")
        return None


# def _rollback_copy(copy_fn: Callable):
#     copied_files = []

#     @functools.wraps(copy_fn)
#     def wrapper(*args, **kwargs):
#         result = copy_fn(*args, **kwargs)
#         if result == None:
#             copied_files.append(args[1])
#         else:
#             print(f"{FONT_BOLD}Rollback copying files: {FONT_RESET}", copied_files)

#         # args_repr = [repr(a) for a in args]
#         # print(f'args copy_to_store:{args_repr}')
#         return result

#     return wrapper


class Config(yaml.YAMLObject):
    """Class for configuration object"""

    yaml_tag = "Config"

    def __init__(self, name: str | None, path_list: list[str]) -> None:
        if name == None:
            self.name = str(uuid.uuid1())
        else:
            self.name = name
        self.files = path_list  # list of configurations paths

        log.info("Create Config object: %s", self)

    def __repr__(self) -> str:
        return "Config(name=%s, files=%s)" % (self.name, self.files)

    def __str__(self) -> str:
        return repr(self)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, value):
        self._files = value

    def rename(self, name: str):
        """Method for rename"""
        self._name = name

    def remove_config(self, path: str) -> bool:
        search_path = pathlib.Path(path)
        log.info(f"Desired file path {search_path}")

        new_path_list = list(
            filter(
                lambda file_path: search_path.samefile(os.path.normpath(file_path)),
                self._files,
            )
        )
        if len(self._files) == len(new_path_list):
            return False
        else:
            self._files = new_path_list
            return True

    def serialize(self) -> dict:
        return dict(name=self.name, files=self.files)


class Repo:
    """Class for handle configurations in the store"""

    def __init__(self, repo_path: str, repo_map_path: str) -> None:
        self.repo_path = repo_path
        self.db_path = repo_map_path
        self.conf_list = []  # list of all configurations objects (Config)
        self.load()

    def __repr__(self) -> str:
        return f"{self._conf_list}"

    @property
    def conf_list(self):
        return self._conf_list

    @conf_list.setter
    def conf_list(self, value: list[Config]):
        self._conf_list = value

    def create(self):
        """Function create empty repository file"""
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                f.write("# Repository of dot files tracker")
        except OSError as e:
            print(f"{FONT_BOLD}Error create repository file: {FONT_RED}{e}{FONT_RESET}")
        finally:
            print(f"{FONT_BOLD}Repository file created{FONT_RESET}")

    def load(self):
        """Load Store object from file"""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                yml = yaml.safe_load_all(f)
                for item in yml:
                    config = Config(item["name"], item["files"])
                    self.conf_list.append(config)
        except OSError as e:
            print(
                f"{FONT_BOLD}Error open exist file repository configurations: {FONT_RED}{e}{FONT_RESET}"
            )

    def add_config(self, config: Config) -> None:
        """Add element to list of configurations"""

        self.conf_list.append(config)
        log.info("dotfiles added: %s", config.files)

    def get_conf_list(self) -> list[Config]:
        """Get list of all configurations"""
        conf_list: list[Config] = []
        conf_list = self.conf_list
        return conf_list

    def get_conf_by_filename(self, path: str) -> list:
        """Search Config object by filename"""
        searched = []
        for config in self.conf_list:
            path_list = config.files
            result = filter(
                lambda p: os.path.abspath(path) == os.path.abspath(p), path_list
            )

            searched.extend(result)
        return searched

    def save(self):
        """Dump Store object to disk as YML"""

        configs = []
        for doc in self.conf_list:
            configs.append(doc.serialize())

        # yaml.emitter.Emitter.process_tag = lambda self, *args, **kw: None

        try:
            with open(self.db_path, "w", encoding="utf-8") as file:
                yaml.dump_all(
                    configs,
                    file,
                    allow_unicode=True,
                    sort_keys=False,
                    Dumper=yaml.Dumper,
                )
        except Exception as e:
            print(
                f"{FONT_BOLD}Error in the process of writing a mapping file: {FONT_RED}{e}{FONT_RESET}"
            )
            exit(1)

    # @_rollback_copy
    def copy_to_store(self, src: str, overwrite: bool = False) -> Exception | None:
        """Copy files or dirs to store preserve permittion, bits and other metadata"""
        dst_path = self.repo_path + os.path.basename(src)
        dst = pathlib.Path(dst_path)
        if dst.exists() and overwrite == False:
            print(
                f"{FONT_BOLD}The file or dir already exist in the store: {FONT_RESET}",
                src,
            )
            exit(1)
        else:
            if dst.is_file:
                try:
                    dst_path = shutil.copy2(src, dst_path, follow_symlinks=True)
                    shutil.copystat(src, dst_path, follow_symlinks=True)
                except Exception as e:
                    print(f"{FONT_BOLD}Error copying file: {FONT_RED}{e}")
                    return e
            if dst.is_dir():
                try:
                    dst_path = shutil.copytree(
                        src,
                        self.repo_path,
                        dirs_exist_ok=True,
                        copy_function=shutil.copy2,
                    )
                    shutil.copystat(src, dst_path)
                except Exception as e:
                    print(f"{FONT_BOLD}Error copying directory: {FONT_RED}{e}")
                    return e

    def rename_group(self, name: str, new_name: str) -> None:
        renamed = False

        for config in self._conf_list:
            if config.name == name:
                config.rename(new_name)
                self.save()
                renamed = True
                break

        if renamed:
            print(f"Group {name} renamed to the {new_name}")
        else:
            print("Nothing rename")
        exit(0)

    def remove_group(self, name: str) -> bool:
        new_conf_list = list(
            filter(lambda config: config.name != name, self._conf_list)
        )
        if len(new_conf_list) == len(self._conf_list):
            return False
        else:
            self._conf_list = new_conf_list
            return True


def add_dotfiles(args, repo: Repo) -> None:
    dotfiles_paths = args.f
    if args.g:
        name = args.g
    else:
        name = None

    dotfiles_paths = [os.path.abspath(path) for path in dotfiles_paths]
    config = Config(name, dotfiles_paths)

    seached_configs = []

    for item in config.files:
        seached_configs.extend(repo.get_conf_by_filename(item))

    if len(seached_configs) == 0 or args.o:
        repo.add_config(config)
        for dotfile_path in config.files:
            repo.copy_to_store(dotfile_path, overwrite=True)
        repo.save()
        print(
            f"{FONT_BOLD}Track files and copy to the repository:{FONT_RESET} {config.files}"
        )
    else:
        print(
            f"{FONT_BOLD}Same dotfile already tracking:{FONT_RESET} {seached_configs}"
        )
        exit(1)


def list_stored_dotfiles(args, repo: Repo) -> None:
    conf_list = repo.get_conf_list()

    for config in conf_list:
        print(f"{FONT_BOLD}{config.name}:")
        print(f"{FONT_RESET}  files: ")
        for filepath in config.files:
            print(f"    {filepath}")


def rename_group(args, repo: Repo) -> None:
    repo.rename_group(args.o, args.n)


def remove(args, repo: Repo) -> None:
    if args.g != None and args.f == None:
        result = repo.remove_group(args.g)
        if result:
            repo.save()
            log.info(f"Remove group {args.g}")
        else:
            print(f"{FONT_BOLD}{args.g}{FONT_RESET} there is no such group")

    if args.g != None and args.f != None:
        for config in repo._conf_list:
            if config.name == args.g:
                if config.remove_config(args.f):
                    repo.save()
                    log.info(f"Remove dotfiles: {args.f} from group {args.g}")
                else:
                    print(
                        f"{FONT_BOLD}{args.f}{FONT_RESET} there is no such file in this group"
                    )


handlers_arg = {
    "add": add_dotfiles,
    "list": list_stored_dotfiles,
    "rename": rename_group,
    "remove": remove,
}


def main():
    config = load_config("~/.dot_tracker.toml")
    if config:
        dotfiles_path = config["general"]["dotfiles"]
        dotfiles_repo = config["general"]["repo_file"]
    else:
        print("The configuration does not exist, please create configuration file")
        exit(0)

    repo = Repo(dotfiles_path, dotfiles_repo)

    parser = argparse.ArgumentParser(description="Working with dotfiles")
    subparsers = parser.add_subparsers(required=True, dest="func_name")

    parser_add = subparsers.add_parser(
        "add", description="add file/dir to repository and track it"
    )
    parser_add.add_argument(
        "-f",
        required=True,
        nargs="*",
        type=pathlib.Path,
        help="path to file or dir",
        metavar="file",
    )
    parser_add.add_argument(
        "-g",
        type=str,
        metavar="group name",
        help="id or name of group dotfiles for one app, default value is random uuid",
    )
    parser_add.add_argument("-o", action="store_true", help="overwrite saved files")

    parser_update = subparsers.add_parser(
        "update", description="update file in the repository"
    )

    parser_rename = subparsers.add_parser("rename", description="rename group of files")
    parser_rename.add_argument(
        "-o", type=str, metavar="name", required=True, help="old group name"
    )
    parser_rename.add_argument(
        "-n", type=str, metavar="name", required=True, help="new group name"
    )

    parser_list = subparsers.add_parser(
        "list", description="get a list of saved configurations"
    )

    parser_remove = subparsers.add_parser(
        "remove", description="remove dotfiles group or files from the repository"
    )
    parser_remove.add_argument(
        "-g",
        type=str,
        required=True,
        help="name of the dotfiles group",
        metavar="group",
    )
    parser_remove.add_argument(
        "-f",
        type=pathlib.Path,
        required=False,
        help="name of the file",
        metavar="file",
    )

    args = parser.parse_args()
    handler = handlers_arg[args.func_name]
    handler(args, repo)


if __name__ == "__main__":
    main()
