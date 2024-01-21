import io
from typing import Generator


class SizeTooBigException(ValueError):
    pass


class File:
    """File object in a FileSystem.

    Initialise with folder: Folder, size: int, name: str.

    Attributes
    ==========
        folder (Folder): parent folder
        size (int): file size
        name (str): file name
    """

    def __init__(self, folder, size, name):
        self.folder = folder
        self.size = int(size)
        self.name = name

    def __str__(self) -> str:
        return f"- {self.name} (file, size={self.size})"


class Folder:
    """
    Folder object in a FileSystem.

    Initialise with parent: Folder, name: str.

    Attributes
    ==========
        parent (Folder): parent folder
        name (str): folder name
        files (dict): dict of files as {filen_ame: file_object}
        folders (dict): dict of folders as {folder_name: folder_object}
    """

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.files = dict()
        self.folders = dict()
        self._size = None
        self._size_exceeded = False

    def __str__(self) -> str:
        return f"- {self.name} (dir)"

    def size(self) -> int:
        """Size of folder, contents and subfolders."""
        if self._size is not None:
            return self._size
        self._size = sum(file.size for file in self.files.values()) + sum(
            folder.size for folder in self.folders.values()
        )
        return self._size

    def _reset_size_under_limit(self, limit=None):
        if self._size is not None and self._size > limit:
            self._size_exceeded = True
            return
        self._size_exceeded = False

    def size_under_limit(self, limit: int):
        """Size of folder, contents and subfolders. Raises SizeTooBigException if size > limit."""
        # size has already been exceeded
        if self._size_exceeded:
            raise SizeTooBigException()

        # calculate size if not already calculated
        if self._size is None:
            try:
                size = 0
                # check the subfolders for size and catch violations
                # do this first to catch exceptions faster
                size += sum(
                    folder.size_under_limit(limit) for folder in self.folders.values()
                )
                # get file size
                size += sum(file.size for file in self.files.values())
                # check size exceeding limit in next section
                self._size = size
            except SizeTooBigException:
                self._size_exceeded = True
                raise SizeTooBigException()

        # size exceeds the limit
        if self._size > limit:
            self._size_exceeded = True
            raise SizeTooBigException()

        return self._size

    def tree(self, indentation: int = 0, result=None) -> str:
        """Return multiline tree str representing folder contents and subfolders."""
        # initialise the result buffer if required
        result = result or io.StringIO()
        # add information about this folder
        result.write(" " * indentation)
        result.write(str(self))
        result.write("\n")
        # increase indentation for this folder's contents
        indentation += 2
        # add information about subfolders
        for folder in self.folders.values():
            # RECURSION
            folder.tree(indentation, result)
        # add information about files
        for file in self.files.values():
            result.write(" " * indentation)
            result.write(str(file))
            result.write("\n")
        # collect result to str
        return result.getvalue()


class FileSystem:
    """
    FileSystem.

    Initialise with optional name (str) for root folder.

    Attributes
    ==========
        root (Folder): root folder
        cwd (Folder): current working folder
    """

    def __init__(self, root_name="/"):
        # initialise variables
        self.files = list()
        self.folders = list()
        self.cwd = None
        self.root = None
        # initialise the root directory
        self.add_root(name=root_name)

    def add_root(self, name="/"):
        """Initialise a root folder."""
        folder = Folder(None, name)
        self.folders.append(folder)
        self.root = folder
        # change directory to root
        self.cwd = folder

    def interpret_commands(self, commands: str) -> None:
        """Interpret command output to build filesystem structure."""
        # create iter for commands
        command_iter = io.StringIO(commands)

        # already initalise the root folder on object creation so skip until after $ cd /
        command = ""
        while not command == "$ cd /":
            command = next(command_iter).strip()

        # get command
        command = next(command_iter).strip()
        while command:
            # list folder contents
            if command == "$ ls":
                # initialise list to hold contents
                directory_contents = list()
                # get contents info
                command = next(command_iter).strip()
                # continue until next prompt
                while "$" not in command:
                    # add the content to the list
                    directory_contents.append(command)
                    # look for next command
                    try:
                        command = next(command_iter).strip()
                    except StopIteration:
                        command = ""
                        break
                # process the sotred folder contents
                for item in directory_contents:
                    # add folder
                    if item.startswith("dir"):
                        folder = Folder(self.cwd, item[4:])
                        self.folders.append(folder)
                        self.cwd.folders[folder.name] = folder
                    # add file
                    else:
                        file = File(self.cwd, *item.split())
                        self.files.append(file)
                        self.cwd.files[file.name] = file
                continue

            # change directory
            if command.startswith("$ cd"):
                # get target
                target_dir = command[5:]
                # target = .. -> change to parent directory
                if target_dir == "..":
                    self.cwd = self.cwd.parent
                # target has name -> change to named directory
                else:
                    self.cwd = self.cwd.folders[target_dir]
                # get next command
                command = next(command_iter).strip()
                continue

    def total_file_size(self) -> int:
        """Size of all files."""
        return sum(file.size for file in self.files)

    def folders_under_size_limit(self, limit: int) -> Generator["Folder", None, None]:
        """Generator yielding folders under specified size limit."""
        # reset the limit information
        for folder in self.folders:
            folder._reset_size_under_limit(limit)
        # process all folders
        # N.B. processing descends into directories as we go
        for folder in self.folders:
            try:
                # yield the size
                folder.size_under_limit(limit)
                yield folder
            # exception raised if size is too big, so continue
            except SizeTooBigException:
                continue

    def tree(self, indentation: int = 0) -> str:
        """Return multiline tree str representing root folder contents and subfolders. See Folder.tree()"""
        return self.root.tree(indentation=indentation)


def go():
    data_list = list()

    from DataSample import DAY_07 as SAMPLE

    data_list.append(("Sample", SAMPLE))
    try:
        from DataFull_ import DAY_07 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    DISK_SPACE = 70000000
    UPDATE_REQUIRES = 30000000

    for name, data in data_list:
        print(name)
        fs = FileSystem()
        fs.interpret_commands(data)
        if "Sample" in name:
            print(fs.tree(indentation=2))
        limit = 100000
        print(
            f"  Total size of folders under {limit}:",
            sum(f._size for f in fs.folders_under_size_limit(100000)),
        )
        total_size = fs.total_file_size()
        print("  Total file size:", total_size)
        space_required = UPDATE_REQUIRES + total_size - DISK_SPACE
        print("  Space required:", space_required)
        too_small = set(fs.folders_under_size_limit(space_required))
        # increase limit of search until find some directories to delete
        for n in range(space_required, DISK_SPACE, 1000):
            n = 1e11
            potential_for_deletion = set(fs.folders_under_size_limit(n)) - too_small
            if potential_for_deletion:
                break
        else:
            raise ValueError("Could not find valid deletion target")
        deletion_target = sorted(potential_for_deletion, key=lambda f: f._size)[0]
        print(
            "Smallest target for deletion is",
            deletion_target.name,
            "with size",
            deletion_target._size,
        )
        print()


if __name__ == "__main__":
    go()
