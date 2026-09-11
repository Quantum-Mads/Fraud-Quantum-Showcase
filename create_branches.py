import subprocess
import sys

def run_git_command(command):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def main():
    # 1. Check if we are inside a Git repository
    is_repo = run_git_command(["git", "rev-parse", "--is-inside-work-tree"])
    if is_repo is None:
        print("Error: This directory is not a Git repository.", file=sys.stderr)
        sys.exit(1)

    # 2. Check if the repository has at least one commit
    has_commits = run_git_command(["git", "rev-parse", "--verify", "HEAD"])
    if has_commits is None:
        print("Error: The repository is empty. Please make at least one commit first.", file=sys.stderr)
        sys.exit(1)

    # 3. Check if 'origin' remote exists
    has_remote = run_git_command(["git", "remote", "get-url", "origin"])
    if has_remote is None:
        print("Warning: No remote named 'origin' found. Branches will only be created locally.")

    branches = ["pre-prod", "dev"]

    for branch in branches:
        # Check if the branch already exists locally
        local_exists = run_git_command(["git", "show-ref", f"refs/heads/{branch}"])
        
        if local_exists:
            print(f"Branch '{branch}' already exists locally.")
        else:
            # Create the branch locally
            created = run_git_command(["git", "branch", branch])
            if created is not None:
                print(f"Branch '{branch}' successfully created locally.")

        # Push to GitHub (if remote 'origin' exists)
        if has_remote:
            print(f"Pushing '{branch}' to GitHub (origin)...")
            pushed = run_git_command(["git", "push", "-u", "origin", branch])
            if pushed is not None:
                print(f"Branch '{branch}' is now live on GitHub.")
            else:
                print(f"Failed to push '{branch}' to GitHub. Check your internet connection or permissions.")

if __name__ == "__main__":
    main()

