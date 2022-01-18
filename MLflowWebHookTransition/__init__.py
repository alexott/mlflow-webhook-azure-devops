import logging

import azure.functions as func

from msrest.authentication import BasicAuthentication

from azure.devops.connection import Connection
from azure.devops.v6_0.pipelines.models import RunPipelineParameters,Variable

def create_error(msg):
    func.HttpResponse(msg, status_code=400)

personal_access_token = ''
organization_url = 'https://dev.azure.com/alexeyottdb/'
project = 'MLFlowHooks'

def maybe_trigger_action(req_body: dict):

    to_stage = req_body.get("to_stage", "")
    from_stage = req_body.get("from_stage", "")
    model_name = req_body["model_name"]
    model_version = req_body.get("version", "0")
    wh_id = req_body["webhook_id"]
    timestamp = req_body["event_timestamp"]
    payload_text = req_body.get("text", "")

    action = "None"

    credentials = BasicAuthentication('', personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)
    pipeline_client=connection.clients_v6_0.get_pipelines_client()
    
    pipeline_id = -1

    variables={
        'model_name': Variable(value=model_name),
        'version': Variable(value=model_version),
        'webhook_id': Variable(value=wh_id),
        'timestamp': Variable(value=timestamp),
        'text': Variable(value=payload_text),
        'stage': Variable(value=to_stage)
    }
    run_parameters=RunPipelineParameters(variables=variables)
    logging.info("Going to trigger build with parameters: %s", run_parameters)

    if to_stage == "Staging" and not from_stage == "Production":
        logging.info("Going to trigger integration pipeline")

        pipeline_id = 3
        
        action = f"Integration test is triggered."

    if to_stage == "Production":
        logging.info("Going to trigger release pipeline")
        # 
        #pipeline_id = 3 

        action = "Deployment to Azure ML triggered."

    if pipeline_id != -1:
        # Run pipeline
        run_pipeline = pipeline_client.run_pipeline(
            run_parameters=run_parameters,
            project=project,
            pipeline_id=pipeline_id)

        action = action + f' Status: {run_pipeline}'

    return action

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if (req.method != "POST"):
        logging.error('It should be POST request!')
        return create_error("It should be POST request!")

    try:
        req_body = req.get_json()
        logging.info("Request body: %s", req_body)
    except ValueError:
        logging.error('Can\'t parse JSON payload')
        return create_error("Can't parse JSON payload")

    try:
        event = req_body["event"]
        model_name = req_body["model_name"]
        model_version = req_body.get("version", "0")
    except Exception:
        logging.error("Can't extract data from payload")
        return create_error("Can't extract data from payload")

    ret_str = f"Processing event: {event} for model {model_name} with version {model_version}"

    if event == "MODEL_VERSION_TRANSITIONED_STAGE":
        ret_str = ret_str + ". Action: " + maybe_trigger_action(req_body)

    logging.info(ret_str)
    return func.HttpResponse(ret_str)
