This repository contains an example of the integration of MLflow with Azure DevOps by using the Azure Function as intermediate layer to workaround lack of support for authentication headers, etc.

## Create Databricks job

Create a job that will be triggered from CI/CD pipeline.  This job will accept a number of parameters, such as model name, version, etc.
You can use [az-devops-setup/ExecuteDevOpsTrigger.py](az-devops-setup/ExecuteDevOpsTrigger.py) as a base for it.


## Create the CI/CD

Create a new build pipeline using the pipeline definition in the [az-devops-setup/azure-pipelines.yaml](az-devops-setup/azure-pipelines.yaml) file. This pipeline will trigger the job on Databricks - the Databricks host, token, and job ID are configured via pipeline variables.  You need to get the ID of created pipeline & put it into the Azure Function definition.

## Create Azure Function

Use the current folder to create an Azure Function with name `MLflowWebHookTransition` - easiest way to do it is to use VS Code with Azure plugin.  Before putting code into active state, put into `__init__.py` ID of Azure DevOps pipeline, URL of DevOps space & personal access token for it (it just needs to be able to read pipeline & trigger the job).


## Register the webhook

Use `curl` to create actual webhook:

```sh
MODEL_NAME='aott-wine-model'
PAT="...." # change it to your personal token
DBHOST="https://eastus2.azuredatabricks.net"
AZFUNC='aott-mlflow-hook-1'
AZHOOKNAME='MLflowWebHookTransition'

#curl -H "Authorization: Bearer $PAT" "$DBHOST/api/2.0/mlflow/registry-webhooks/list?model_name=$MODEL_NAME"
curl -H "Authorization: Bearer $PAT" "$DBHOST/api/2.0/mlflow/registry-webhooks/create" -X POST -d "{\"model_name\": \"$MODEL_NAME\", \"events\": [\"MODEL_VERSION_TRANSITIONED_STAGE\"], \"description\": \"Test for $MODEL_NAME\", \"http_url_spec\": { \"url\": \"https://${AZFUNC}.azurewebsites.net/api/${AZHOOKNAME}\"}}"
```
