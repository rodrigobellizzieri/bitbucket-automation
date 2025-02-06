import requests as r
import os
import json
import subprocess
import shutil

# Default variables
workspace = os.getenv("BITBUCKET_WORKSPACE") # From Workspace
project = os.getenv("PROJECT") # From pipeline
repository = os.getenv("REPOSITORY") # From pipeline
template = os.getenv("TEMPLATE") # From pipeline
private = os.getenv("PRIVATE") # From pipeline
main_branche = os.getenv("MAIN_BRANCHE") # From pipeline
dev_branche = os.getenv("DEV_BRANCHE") # From pipeline
ci_email = os.getenv("CI_EMAIL") # From Workspace
ci_name = os.getenv("CI_NAME") # From Workspace
bb_user = os.getenv("BITBUCKET_USER") # From Workspace
app_pass = os.getenv("BITBUCKET_PASS") # From Workspace

#Auth variables (OAuth Consumer)
client_id = os.getenv("OAUTH_CLIENT_ID")
client_secret = os.getenv("OAUTH_CLIENT_SECRET")

#Default url variables
token_url = "https://bitbucket.org/site/oauth2/access_token"


# Validate and Format variables
check_vars = {"BITBUCKET_WORKSPACE": workspace,
              "PROJECT": project,
              "REPOSITORY": repository,
              "TEMPLATE": template,
              "CI_EMAIL": ci_email,
              "CI_NAME": ci_name,
              "BITBUCKET_USER": bb_user,
              "BITBUCKET_PASS": app_pass,
              "OAUTH_KEY": client_id,
              "OAUTH_SECRET": client_secret,
              "PRIVATE": private,
              "MAIN_BRANCHE": main_branche,
              "DEV_BRANCHE": dev_branche,
              }

for name, var in check_vars.items():
    if var is None:
        print(f"Error to get variables value: {name} - None")
        exit(1)

repository = repository.lower()
project = project.upper()
private = private.lower()
url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repository}"


# Get token
def getToken():
    response = r.post(
        token_url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret)
    )

    if response.status_code == 200:
        token = response.json().get("access_token")
    else:
        print(f"Get token error: {response.json()}")
        exit(1)

    return token

# Set token
token = getToken()

# Create Repository
def createRepository(repository):

    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
    }

    if private == "public":
        payload = json.dumps( {
            "is_private": False,
            "project": {
                "key": f"{project}"
            },
            "mainbranch": {"name": main_branche}
            } ) 
    elif private == "private":
        payload = json.dumps( {
            "is_private": True,
            "project": {
                "key": f"{project}"
            },
            "mainbranch": {"name": main_branche}
            } )
    else:
        print("Error: This value is not allowed")

    response = r.request(
    "POST",
    url,
    data=payload,
    headers=headers
    )

    if response.status_code == 200:
        print("Created Successfully ✅")
    else:
        print(f"Unfortanetally we can't create this repository ❌")
        print(f"Status Code: {response.status_code}")
        print(response.json())
        exit(1)
    
    return repository


# Set template and configure repository
def cloneRepository():
    repo_url = f"https://{bb_user}:{app_pass}@bitbucket.org/{workspace}/{repository}.git"
    subprocess.run(["git", "clone", repo_url])


def setTemplate():
    current_path = os.getcwd()
    template_path = os.path.join(current_path, "templates", template)
    repo_path = os.path.join(current_path, repository)

    # Copy template
    shutil.copytree(template_path, repo_path, dirs_exist_ok=True)


def pushTemplate():
    repo_path = os.path.join(os.getcwd(), repository)
    subprocess.run(["git", "config", "--global", "user.email", f"{ci_email}"])
    subprocess.run(["git", "config", "--global", "user.name", f"{ci_name}"])
    subprocess.run(["git", "-C", repo_path, "add", "."])
    subprocess.run(["git", "-C", repo_path, "commit", "-m", f"Add template {template}"])
    subprocess.run(["git", "-C", repo_path, "push"])
    
    # Create branche dev
    subprocess.run(["git", "-C", repo_path, "pull"])
    subprocess.run(["git", "-C", repo_path, "checkout", "-b", f"{dev_branche}"])
    subprocess.run(["git", "-C", repo_path, "add", "."])
    subprocess.run(["git", "-C", repo_path, "commit", "-m", f"Add branche {dev_branche}"])
    subprocess.run(["git", "-C", repo_path, "push", "--set-upstream", "origin", f"{dev_branche}"])


# Start functions
createRepository(repository)
cloneRepository()
setTemplate()
pushTemplate()

print(85 * "=")
print(f"Made with many coffee by Rodrigo Bellizzieri")
print(f'Repository URL: https://bitbucket.org/{workspace}/{repository}/')
print(85 * "=")