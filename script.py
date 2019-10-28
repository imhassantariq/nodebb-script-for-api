import argparse
import uuid
import requests
import json


NODEBB_WRITE_API_MASTER_TOKEN = "d05d259f-08f9-450f-aaa4-975cdd83ba52"
NOBEE_API_URL = "http://localhost:4568/api/v2"


def parse_arguments():
    """This Function checks for command line arguments and parse it"""
    arg = argparse.ArgumentParser()
    arg.add_argument("-c", "--categories",
                     help="Number of Categories you want to create", type=int)
    arg.add_argument("-t", "--topics",
                     help="Number of topics you want to create in each category", type=int, default=0)
    arg.add_argument("-r", "--replies",
                     help="Number of replies you want to post in each topic", type=int, default=0)
    arg.add_argument("-u", "--users",
                     help="Number of users you want to create", type=int)
    arg_values = vars(arg.parse_args())
    return arg_values


def create_categories(num_of_categories):
    list_of_categories = {}
    for num in range(0, num_of_categories):
        category_name = uuid.uuid4()
        data = {
            'name': "test-" + str(category_name)
        }
        status, response, seconds_took = _call('/categories', **data)
        if status:
            payload = response['payload']
            list_of_categories[payload['cid']] = response
            print("Category with id:{} created and took {} seconds".format(payload['cid'], seconds_took))
    return list_of_categories


def create_topics(list_of_categories, num_of_topics):
    list_of_topic_id = []
    for category in list_of_categories:
        for num in range(0, num_of_topics):
            topic_uuid = str(uuid.uuid4())
            topic_title = '{}-topic-{}'.format(list_of_categories[category]['payload']['name'], topic_uuid)
            topic_content = '{}-description-{}'.format(list_of_categories[category]['payload']['name'], topic_uuid)
            data = {
                'cid': category,
                'title': topic_title,
                'content': topic_content
            }
            status, response, seconds_took = _call('/topics', **data)
            if status:
                payload = response['payload']
                print("Topic with id:{} in Category with id:{} is created and took {} seconds.".format(
                    payload['topicData']['tid'], payload['topicData']['cid'], seconds_took))
                list_of_topic_id.append(payload['topicData']['tid'])

    return list_of_topic_id


def post_replies(list_of_topic_ids, num_of_replies):
    list_of_post_id = []
    for topic_id in list_of_topic_ids:
        for num in range(0, num_of_replies):
            reply_uuid = str(uuid.uuid4())
            reply_content = "{}: reply in topic: {}".format(num+1, topic_id)
            data = {
                'content': reply_content
            }
            status, response, seconds_took = _call('/topics/{}'.format(topic_id), **data)
            if status:
                payload = response['payload']
                print("Post with id:{} on Topic with id:{} in Category with id:{} is posted and took {} seconds.".format(
                    payload['pid'], payload['tid'], payload['cid'], seconds_took))
                list_of_post_id.append(payload['pid'])
    return list_of_post_id


def create_users(num_of_users):
    list_of_users = []
    for num in range(0, num_of_users):
        user_name = uuid.uuid4()
        data = {
            'username': "test-user-" + str(user_name)
        }
        status, response, seconds_took = _call('/users', **data)
        if status:
                payload = response['payload']
                print("User with id:{} created and took {} seconds.".format(payload['uid'], seconds_took))
                list_of_users.append({payload['uid']: payload})
    return list_of_users


def _call(path, **kwargs):
    kwargs['_uid'] = 1
    headers = {
        'Authorization': "Bearer {}".format(NODEBB_WRITE_API_MASTER_TOKEN),
        'Content-Type': 'application/json'
    }
    url = NOBEE_API_URL + path
    response = requests.request("POST", url, data=json.dumps(kwargs), headers=headers)
    seconds_took = response.elapsed.total_seconds()
    if response.status_code == 200:
        return True, response.json(), seconds_took
    return False, response.json(), str(seconds_took)


if __name__ == "__main__":
    arguments = parse_arguments()
    if arguments['categories']:
        list_of_categories = create_categories(arguments['categories'])
        list_of_topic_id = create_topics(list_of_categories, arguments['topics'])
        list_of_replies_id = post_replies(list_of_topic_id, arguments['replies'])

    if arguments['users']:
        list_of_users = create_users(arguments['users'])
