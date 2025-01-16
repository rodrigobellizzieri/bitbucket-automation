import os
import json
import shutil
import requests as r
import subprocess


# ==================== Helper Functions ==================== #

def validate_variables(variables):
    """Validate that all required environment variables are set."""
    for name, var in variables.items():
        if var is None:
            print(f"Error: Missing required environment variable: {name}")
            exit(1)


def execute_subprocess(commands, repo_path=None, error_message="Subprocess failed"):
    """Execute a subprocess command with error handling."""
    result = subprocess.run(
        commands,
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"{error_message}: {result.stderr.strip()}")
        exit(1)


def get_headers(token):
    """Return the default headers for API requests."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


# ==================== Core Functions ==================== #

def get_token(client_id, client_secret):
    """Get an OAuth token from Bitbucket."""
    response = r.post(
        token_url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret)
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error obtaining token: {response.json()}")
        exit(1)


def create_repository(repository_name):
    """Create a new repository in Bitbucket."""
    payload = {
        "is_private": private == "private",
        "project": {"key": project},
        "mainbranch": {"name": "main"}
    }
    response = r.post(url, json=payload, headers=get_headers(token))
    if response.status_code == 200:
        print("Repository created successfully ✅")
    else:
        print("Failed to create repository ❌")
        print(f"Status Code: {response.status_code}")
        print(response.json())
        exit(1)


def clone_and_setup_branches():
    """Clone the repository and set up main and develop branches."""
    repo_url = f"https://{bb_user}:{app_pass}@bitbucket.org/{workspace}/{repository}.git"

    # Clone the repository
    execute_subprocess(["git", "clone", repo_url], error_message="Error cloning repository")

    repo_path = os.path.join(os.getcwd(), repository)

    # Configure Git user details
    execute_subprocess(["git", "-C", repo_path, "config", "user.email", ci_email])
    execute_subprocess(["git", "-C", repo_path, "config", "user.name", ci_name])

    # Create and push develop branch
    execute_subprocess(["git", "-C", repo_path, "checkout", "-b", "develop"])
    shutil.copytree(os.path.join(os.getcwd(), "templates", template), repo_path, dirs_exist_ok=True)
    execute_subprocess(["git", "-C", repo_path, "add", "."])
    execute_subprocess(["git", "-C", repo_path, "commit", "-m", "Initial commit on develop"])
    execute_subprocess(["git", "-C", repo_path, "push", "--set-upstream", "origin", "develop"])

    # Create and push main branch
    execute_subprocess(["git", "-C", repo_path, "checkout", "-b", "main"])
    execute_subprocess(["git", "-C", repo_path, "push", "--set-upstream", "origin", "main"])

    print("Develop and Main branches created and pushed successfully ✅")


def set_default_branch():
    """Configure the development and production branches in Bitbucket."""
    payload = {
        "development": {"use_mainbranch": False, "name": "develop"},
        "production": {"enabled": True, "use_mainbranch": False, "name": "main"}
    }
    default_branch_url = f"{url}/branching-model/settings"
    response = r.put(default_branch_url, json=payload, headers=get_headers(token))
    if response.status_code == 200:
        print("Branching model updated successfully ✅")
    else:
        print("Failed to update the branching model ❌")
        print(f"Status Code: {response.status_code}")
        print(response.json())
        exit(1)


# ==================== Script Entry Point ==================== #

# Default variables
workspace = os.getenv("BITBUCKET_WORKSPACE")
project = os.getenv("PROJECT")
repository = os.getenv("REPOSITORY")
template = os.getenv("TEMPLATE")
private = os.getenv("PRIVATE")
ci_email = os.getenv("CI_EMAIL")
ci_name = os.getenv("CI_NAME")
bb_user = os.getenv("BITBUCKET_USER")
app_pass = os.getenv("BITBUCKET_PASS")
client_id = os.getenv("OAUTH_CLIENT_ID")
client_secret = os.getenv("OAUTH_CLIENT_SECRET")

# API URLs
token_url = "https://bitbucket.org/site/oauth2/access_token"
url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repository}"

# Validate variables
validate_variables({
    "BITBUCKET_WORKSPACE": workspace,
    "PROJECT": project,
    "REPOSITORY": repository,
    "TEMPLATE": template,
    "CI_EMAIL": ci_email,
    "CI_NAME": ci_name,
    "BITBUCKET_USER": bb_user,
    "BITBUCKET_PASS": app_pass,
    "OAUTH_CLIENT_ID": client_id,
    "OAUTH_CLIENT_SECRET": client_secret,
    "PRIVATE": private
})

# Main logic
token = get_token(client_id, client_secret)
create_repository(repository)
clone_and_setup_branches()
set_default_branch()

print("=" * 85)
print(f"Made with many coffee by Rodrigo Bellizzieri")
print(f"Repository URL: https://bitbucket.org/{workspace}/{repository}/")
print("=" * 85)
