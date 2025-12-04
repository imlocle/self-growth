from controllers.lambda_1_controller import Lambda1Controller
from utils.response_util import success_response, error_response

class Lambda1Handler:
    def __init__(self):
        self.controller = Lambda1Controller()

    def handler(self, event, context):
        try:
            result = self.controller.handle_event(event)
            return success_response(result)
        except Exception as e:
            return error_response(message=str(e))

def lambda_handler(event, context):
    return Lambda1Handler().handler(event, context)