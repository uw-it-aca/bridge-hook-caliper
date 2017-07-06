from caliper.events import AssessmentEvent
from caliper.profiles import AssessmentProfile
from caliper.entities import Person, Assessment
from caliper import HttpOptions, build_sensor_from_config
from django.conf import settings
from django.utils import timezone


def send_event(event):
    config = HttpOptions(host=settings.LRS_ENDPOINT,
                         auth_scheme=u'Bearer',
                         api_key=u"%s" % settings.LRS_API_KEY)

    id = '%s/sensor' % settings.BRIDGE_HOST
    sensor = build_sensor_from_config(sensor_id=id,
                                      config_options=config)

    if settings.DEBUG:
        print sensor._clients.values()[0]._requestor._get_payload_json(event)
    sensor.send(event)


def build_event(json_data):
    if not has_fields(json_data, 'trigger', 'learner', 'enrollment'):
        return

    action = get_action(json_data)
    if not action:
        # Bridge sends a lot of updated actions w/o much context.
        # We only have a caliper event for created and completed
        return

    try:
        event = AssessmentEvent(actor=build_actor(json_data),
                                event_object=build_assessment(json_data),
                                eventTime=get_now(),
                                action=get_action(json_data)
                                )
    except Exception as ex:
        print "Error: ", ex
        return

    return event


def has_fields(json_data, *field_names):
    for field in field_names:
        if field not in json_data:
            return False
    return True


def build_actor(json_data):
    netid = json_data['learner']['uid'].split('@')[0]
    return Person(entity_id=u'https://uw.edu/%s' % netid)


def build_assessment(json_data):
    key = None
    if 'course' in json_data:
        key = 'course'
    elif 'program' in json_data:
        key = 'program'

    if not key:
        raise Exception("Unknown assessment type")

    return Assessment(entity_id=u"%s/%s_id/%s" % (settings.BRIDGE_HOST,
                                                  key,
                                                  json_data[key]['id']),
                      name=json_data[key]['title'])


def get_action(json_data):
    if 'created' == json_data['trigger']:
        return AssessmentProfile._actions['STARTED']
    elif "completed" == json_data['trigger']:
        return AssessmentProfile._actions['SUBMITTED']
    return


def get_now():
    return timezone.now()
