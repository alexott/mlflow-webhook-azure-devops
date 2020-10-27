import logging

import azure.functions as func

def create_error(msg):
    func.HttpResponse(msg, status_code=400)

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
        wh_id = req_body["webhook_id"]
        timestamp = req_body["event_timestamp"]
        model_name = req_body["model_name"]
        model_version = req_body.get("version", "0")
        to_stage = req_body.get("to_stage", "")
        from_stage = req_body.get("from_stage", "")
        payload_text = req_body.get("text", "")
    except:
        logging.error("Can't extract data from payload")
        return create_error("Can't extract data from payload")

    ret_str = f"Processing event: {event} for model {model_name} with version {model_version}"
    logging.info(ret_str)
    return func.HttpResponse(ret_str)
