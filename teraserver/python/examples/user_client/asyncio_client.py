import aiohttp
import asyncio
import json

import opentera.messages.python as messages
from google.protobuf.json_format import ParseDict, ParseError
from google.protobuf.json_format import MessageToJson


login_api_endpoint = '/api/user/login'


async def fetch(client, url, auth=None,  params=None):
    if params is None:
        params = {}
    async with client.get(url, auth=auth, params=params, verify_ssl=False) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            return {}


async def parse_message(client, msg_dict: dict):
    try:
        if 'message' in msg_dict:
            message = ParseDict(msg_dict['message'], messages.TeraEvent(), ignore_unknown_fields=True)
            for any_msg in message.events:
                # Test for DeviceEvent
                device_event = messages.DeviceEvent()
                if any_msg.Unpack(device_event):
                    # TODO Handle device_event
                    print('device_event:', device_event)

                # Test for JoinSessionEvent
                join_session_event = messages.JoinSessionEvent()
                if any_msg.Unpack(join_session_event):
                    # TODO Handle join_session_event
                    print('join_session_event:', join_session_event)

                # Test for ParticipantEvent
                participant_event = messages.ParticipantEvent()
                if any_msg.Unpack(participant_event):
                    # TODO Handle participant_event
                    print('participant_event:', participant_event)

                # Test for StopSessionEvent
                stop_session_event = messages.StopSessionEvent()
                if any_msg.Unpack(stop_session_event):
                    # TODO Handle stop_session_event
                    print('stop_session_event:', stop_session_event)

                # Test for UserEvent
                user_event = messages.UserEvent()
                if any_msg.Unpack(user_event):
                    # TODO Handle user_event
                    print('user_event:', user_event)

                # Test for LeaveSessionEvent
                leave_session_event = messages.LeaveSessionEvent()
                if any_msg.Unpack(leave_session_event):
                    # TODO Handle leave_session_event
                    print('leave_session_event:', leave_session_event)

                # Test for JoinSessionReply
                join_session_reply = messages.JoinSessionReplyEvent()
                if any_msg.Unpack(join_session_reply):
                    # TODO Handle join_session_reply
                    print('join_session_reply:', join_session_reply)

    except ParseError as e:
        print(e)

    return


async def main(url, username, password):

    async with aiohttp.ClientSession() as client:
        params = {}
        login_info = await fetch(client, url + login_api_endpoint, aiohttp.BasicAuth(username, password), params)
        print(login_info)
        if 'websocket_url' in login_info:
            websocket_url = login_info['websocket_url']

            ws = await client.ws_connect(url=websocket_url, ssl=False)
            print(ws)

            while True:
                try:
                    msg = await ws.receive(timeout=1)

                    if msg.type == aiohttp.WSMsgType.text:
                        await parse_message(client, msg.json())
                    if msg.type == aiohttp.WSMsgType.closed:
                        print('websocket closed')
                        break
                    if msg.type == aiohttp.WSMsgType.error:
                        print('websocket error')
                        break
                except asyncio.exceptions.TimeoutError as e:
                    print(e)
                    break

if __name__ == '__main__':

    loop_count = 1000

    for n in range(loop_count):
        print('Client connect, attempt: ', n)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main('https://127.0.0.1:40075', 'admin', 'admin'))

    print('Done!')
