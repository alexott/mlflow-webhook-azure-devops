
This repository contains an example of the integration of MLflow with Azure DevOps via [MLflow Registry webhooks](https://docs.microsoft.com/en-us/azure/databricks/applications/mlflow/model-registry-webhooks?cid=kerryherger), using the Azure Function as intermediate layer to work around the lack of support for authentication headers, custom payload, etc.

## Create Databricks job

This is just for example, as it's easier to trigger Databricks job directly via webhook.

Create a job that will be triggered from CI/CD pipeline.  This job will accept a number of parameters, such as model name, version, etc.
You can use [az-devops-setup/ExecuteDevOpsTrigger.py](az-devops-setup/ExecuteDevOpsTrigger.py) as a base for it.

## Create a CI/CD pipeline

Create a new build pipeline using the pipeline definition in the [az-devops-setup/azure-pipelines.yaml](az-devops-setup/azure-pipelines.yaml) file. This pipeline will trigger the job on Databricks - the Databricks host, token, and job ID are configured via pipeline variables.  You need to get the ID of created pipeline & put it into the Azure Function definition.

## Create Azure Function

Use current folder to create an Azure Function with name `MLflowWebHookTransition` - easiest way to do it is to use VS Code with Azure plugin.  Before putting code into active state, update following variables in `MLflowWebHookTransition/__init__.py` (this is just for example, in reality you need to use Azure KeyVault (for example, as [described here](https://servian.dev/accessing-azure-key-vault-from-python-functions-44d548b49b37))):

* `to_staging_pipeline_id` - ID of Azure DevOps pipeline to trigger when model is transitioned into Staging (except cases when it's moved from Production)
* `to_prod_pipeline_id` - ID of Azure DevOps pipeline to trigger when model is transitioned into Production
* `organization_url` - URL of DevOps space
* `personal_access_token` - personal access token for Azure DevOps (it just needs to be able to read pipeline & trigger the job)

## Register the webhook

Use `curl` to create actual webhook (see [documentation](https://docs.microsoft.com/en-us/azure/databricks/applications/mlflow/model-registry-webhooks?cid=kerryherger) for more information):

```sh
MODEL_NAME='aott-wine-model'
PAT="...." # change it to your Databricks personal access token
DBHOST="https://adb-1234.10.azuredatabricks.net"
AZFUNC='aott-mlflow-hook-1'
AZHOOKNAME='MLflowWebHookTransition'

#curl -H "Authorization: Bearer $PAT" "$DBHOST/api/2.0/mlflow/registry-webhooks/list?model_name=$MODEL_NAME"
curl -H "Authorization: Bearer $PAT" "$DBHOST/api/2.0/mlflow/registry-webhooks/create" -X POST -d "{\"model_name\": \"$MODEL_NAME\", \"events\": [\"MODEL_VERSION_TRANSITIONED_STAGE\"], \"description\": \"Test for $MODEL_NAME\", \"http_url_spec\": { \"url\": \"https://${AZFUNC}.azurewebsites.net/api/${AZHOOKNAME}\"}}"
```
