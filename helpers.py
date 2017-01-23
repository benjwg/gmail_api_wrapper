import tornado.gen

from wrapper import GmailAPI


gmail_api = GmailAPI()


@tornado.gen.coroutine
def fetch_labels():
    '''
    Grabs labels that exist for the account of userId
    '''
    parameters = {
        'resource': 'labels'
    }
    response, error = yield tornado.gen.Task(
        gmail_api.request, parameters=parameters)

    raise tornado.gen.Return((response, error))


@tornado.gen.coroutine
def fetch_latest_email(label_id):
    '''
    Gets emails with a specific label Id
    '''
    parameters = {
        'resource': 'messages',
        'maxResults': 1,
        'labelIds': label_id
    }

    response, error = yield tornado.gen.Task(
        gmail_api.request, parameters=parameters)

    raise tornado.gen.Return((response, error))


@tornado.gen.coroutine
def fetch_email(message_id):
    '''
    Fetch the full API response given a messageId
    '''
    parameters = {
        'resource': 'messages',
        'resource_id': message_id
    }

    response, error = yield tornado.gen.Task(
        gmail_api.request, parameters=parameters)

    raise tornado.gen.Return((response, error))


@tornado.gen.coroutine
def fetch_attachment(message_id, attachment_id):
    '''
    Download the attachments on an email with the included messageId
    '''
    parameters = {
        'resource': 'messages',
        'resource_id': message_id,
        'subresource': 'attachments',
        'subresource_id': attachment_id,
    }

    response, error = yield tornado.gen.Task(
        gmail_api.request, parameters=parameters)

    raise tornado.gen.Return((response, error))
