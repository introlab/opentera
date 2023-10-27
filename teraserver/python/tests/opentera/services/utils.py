import unittest
from flask_restx import Resource, inputs
import time
from opentera.services.ServiceAccessManager import ServiceAccessManager
import opentera.redis.RedisVars as RedisVars
import jwt
import uuid


def infinite_jti_sequence():
    num = 0
    while True:
        yield num
        num += 1


# Initialize generator, call next(user_jti_generator) to get next sequence number
user_jti_generator = infinite_jti_sequence()
participant_jti_generator = infinite_jti_sequence()

@staticmethod
def _generate_fake_user_token(name='FakeUser', user_uuid=str(uuid.uuid4()), roles=[],
                              superadmin=False, expiration=3600):
    # Creating token with user info
    now = time.time()
    token_key = ServiceAccessManager.api_user_token_key

    payload = {
        'iat': int(now),
        'exp': int(now) + expiration,
        'iss': 'TeraServer',
        'jti': next(user_jti_generator),
        'user_uuid': user_uuid,
        'id_user': 1,
        'user_fullname': name,
        'user_superadmin': superadmin,
        'service_access': {'FakeService': roles}  # role of the user
    }

    return jwt.encode(payload, token_key, algorithm='HS256')


@staticmethod
def _generate_fake_static_participant_token(participant_uuid=str(uuid.uuid4())):
    # Creating token with participant info
    token_key = ServiceAccessManager.api_participant_static_token_key
    payload = {
        'iss': 'TeraServer',
        'jti': next(participant_jti_generator),
        'participant_uuid': participant_uuid,
        'id_participant': 1
    }
    return jwt.encode(payload, token_key, algorithm='HS256')


@staticmethod
def _generate_fake_dynamic_participant_token(name='FakeParticipant', participant_uuid=str(uuid.uuid4()),
                                             expiration=3600):
    # Creating token with participant info
    now = time.time()
    token_key = ServiceAccessManager.api_participant_token_key
    payload = {
        'iat': int(now),
        'exp': int(now) + expiration,
        'iss': 'TeraServer',
        'jti': next(participant_jti_generator),
        'participant_uuid': participant_uuid,
        'id_participant': 2,
        'user_fullname': name
    }

    return jwt.encode(payload, token_key, algorithm='HS256')

