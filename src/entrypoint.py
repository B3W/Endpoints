'''Entry point for Endpoints application'''
import inspect
import os
import sys


if __name__ == '__main__':
    # Reference: https://stackoverflow.com/a/6098238
    # Get path to the application's root folder
    file_path = inspect.getfile(inspect.currentframe())
    root_path = os.path.realpath(os.path.abspath(os.path.split(file_path)[0]))

    # Add to sys.path if it is not already there
    path = sys.path

    if root_path not in path:
        sys.path.insert(0, root_path)

    # Add subfolders to path
    packages = ["connection",
                "discovery",
                "message",
                "network",
                "shared",
                "ui"]

    for package in packages:
        package_path = os.path.realpath(os.path.abspath(os.path.join(root_path,
                                                                     package)))
        path = sys.path

        if package_path not in path:
            sys.path.insert(0, package_path)

    # Call main
    import main
    main.main()
