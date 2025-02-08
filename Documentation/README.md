# Development Notes



When this automation fineshe you can see the URL of your new repository.

---

## Workflow
1. **Select Project** ✅  
2. **Set Repository Name** ✅  
5. **Choose Repository Visibility** (Private or Public) ✅  
4. **Select Template** ✅
5. **Set branch PRD name** ✅
6. **Set branch DEV name** ✅
7. **Create Repository** ✅  
8. **Apply Template** ✅  
9. **Finish and Display Repository URL** ✅  

---


# How to use this automation:

## Prerequisites
Before using this project, ensure the following requirements are met:

### **Environment Variables**
The following variables must be configured in your workspace (Bitbucket environment settings):  

- **`CI_EMAIL`**: Email of the Bitbucket user for committing templates.  
- **`CI_NAME`**: Name of the Bitbucket user for committing templates.  
- **`BITBUCKET_USER`**: Bitbucket username for committing templates.  
- **`BITBUCKET_PASS`**: App password for cloning repositories.  

### **OAuth Consumer**
You must create an OAuth Consumer with the following permissions:  
- Admin access to **Projects**.  
- Admin access to **Repositories**.  

Set these OAuth Consumer credentials as repository variables or workspace:  
- **`OAUTH_CLIENT_ID`**: Client ID of the OAuth Consumer.  
- **`OAUTH_CLIENT_SECRET`**: Client Secret of the OAuth Consumer.  

---

## Pipeline Setup
Create a central repository to store the pipeline configuration. This repository must include:  
**1.** A **`templates`** directory containing subdirectories for each template.  
   - The name of the subdirectory must exactly match the template names used in the pipeline variables (e.g., `golang`, `typescript`, `terraform`, `serverlessframework`).  

## Folder Structure Example
The central repository should follow this structure:
```shell
templates/
├── golang/
├── typescript/
├── terraform/
├── serverlessframework/
```

**2.** Copy the **`bitbucket-pipelines.yml`** from example/ to your repository:  


---
## Project Key Setup
Make sure the `KEY` for all projects corresponds to the **allowed-values** in the `PROJECT` variable of the pipeline. Example:

- **DEVOPS**   
- **OPS**  
- **PUB**  
- **REP**  

You can find the project key in Bitbucket's UI under **Projects Page**. The project key must match exactly as defined.
