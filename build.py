import os
import click
import shutil

from git import Repo
from pymed.version import __version__


def clean():
    """ Clean directories that are the result of a build.
    """

    # Loop over the directories that should be deleted
    for directory in ["./build/", "./dist/", "./venv/"]:
        try:
            shutil.rmtree(os.path.abspath(directory))
        except FileNotFoundError as e:
            pass
        except Exception as e:
            raise e


def buildPackage(username, password, production=False):
    """ Method that builds a package and uploads it to PyPi.
    """

    # Make sure we have a clean slate
    clean()

    # Run these OS commands to build and upload the package
    os.system("python setup.py sdist bdist_wheel")
    if production:
        os.system(f"twine upload -u {username} -p {password} --repository pypiprd dist/*")
    else:
        os.system(f"twine upload -u {username} -p {password} --repository pypi dist/*")

    # Clean any mess we made
    clean()


def commitChanges():
    """ Commit any new version file (created by an automatic bump).
    """

    # Get a reference to the Git repo (in this folder)
    repo = Repo(os.path.dirname(__file__))

    # Commit the new version
    repo.git.commit("pymed/version.py", message="Bumped the release version")

    # Push any changes
    repo.git.push("origin", "master")


def bumpVersion(release_type: str = "revision", direction: int = 1):
    """ Bump the version number in the version file.
    """

    # Parse the current version
    major, minor, revision = __version__.split(".")

    # Increase (or decrease) the number
    if release_type == "major":
        major = int(major) + direction
    if release_type == "minor":
        minor = int(minor) + direction
    if release_type == "revision":
        revision = int(revision) + direction

    # Assemble the new version number
    new_version = f"{major}.{minor}.{revision}"

    # Open the version file and save the new version number
    with open("pymed/version.py", "w") as version_file:
        version_file.write(f"""__version__ = "{new_version}"\n""")

    # Return the new version
    return new_version


@click.command()
@click.option("--username", "-u", help="Username to publish to PyPi")
@click.option("--password", "-p", help="Password for publishing to PyPi")
@click.option(
    "--release_type", "-t", default="revision", help="Type of release to build"
)
@click.option("--production/--no-production", default=False)
def build(release_type, username, password, production):
    """ Method that chains together the bumping of the version, committing the change and pushing the new package.
    """

    # Check the input
    if release_type not in ["major", "minor", "revision"]:
        raise Exception(
            "Unknown release type, choose one of the following: 'major', 'minor', or 'revision'"
        )

    # Bump the version
    new_version = bumpVersion(release_type=release_type)
    print(f"Bumping the version. New version is: {new_version}")

    # Commit changes to Git
    print("Commit and push changes to Git")
    commitChanges()

    print("Build the package and upload it to PyPi")
    buildPackage(username=username, password=password, production=production)


if __name__ == "__main__":
    build()
