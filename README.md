# Bitbucket Automation Project

## Overview
This project automates the creation of repositories in Bitbucket, configuring templates, repository visibility, and other settings seamlessly through a Bitbucket Pipeline.

## Features Included
This project automates the creation of repositories on Bitbucket, allowing you to:    
- Apply a predefined template files.
- Toggle repository visibility (private/public).
- Create base branches to dev and prd environments and set branch model.
- Enable pipelines 

---

## New fetures in this version 1.0.0
- [x] Create a `production` branch.  
- [x] Create a `development` branch.  
- [x] Enable pipeline.

---

## Usage Instructions - Read the  README on Documentation/
1. **Configure Environment Variables:**  
   Ensure all required variables are set in the workspace settings.  

2. **Prepare the Pipeline:**  
   Commit the `bitbucket-pipelines.yml` file to the central repository.  

3. **Add Template Files:**  
   Include your template files in the `templates` directory within the central repository.  

4. **Run the Pipeline:**  
   Execute the custom pipeline `bitbucket-automation` via the Bitbucket UI or API, providing the necessary variables:
   - **`PROJECT`**: The project key.  
   - **`REPOSITORY`**: The name of the new repository.  
   - **`PRIVATE`**: Specify `True` for private or `False` for public visibility.  
   - **`TEMPLATE`**: The selected repository template. 
   - **`PRD_BRANCH`**: Branch to set in production.
   - **`DEV_BRANCH`**: Branch to set in development. 

---
## Feel free to open an issue, pull request or contact me if you need help or have suggestions for extending this automation. Happy automating! ☕️
