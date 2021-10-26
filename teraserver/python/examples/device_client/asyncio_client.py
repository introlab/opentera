import aiohttp
import asyncio
import json
from signal import SIGINT, SIGTERM
import time

import opentera.messages.python as messages
from google.protobuf.json_format import ParseDict, ParseError
from google.protobuf.json_format import MessageToJson

login_api_endpoint = '/api/device/login'
status_api_endpoint = '/api/device/status'


async def fetch(client, url, params=None):
    if params is None:
        params = {}
    async with client.get(url, params=params, verify_ssl=False) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            return {}


async def send_device_status(client: aiohttp.ClientSession, url: str, token: str):
    while True:
        try:
            # Every 10 seconds
            await asyncio.sleep(60)
            params = {'token': token}

            from datetime import datetime

            # This can be anything...
            status = {
                'status': {'battery': 10.4, 'charging': False},
                'timestamp': datetime.now().timestamp()
            }

            async with client.post(url, params=params, json=status, verify_ssl=False) as response:
                if response.status == 200:
                    print('Sent status ok', status)
                else:
                    print('Send status failed', response)
                    raise Exception('Status cannot be sent')
        except asyncio.CancelledError as e:
            print('send_device_status cancelled', e)
            # Exit loop
            break


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
                    continue

                # Test for JoinSessionEvent
                join_session_event = messages.JoinSessionEvent()
                if any_msg.Unpack(join_session_event):
                    # TODO Handle join_session_event
                    print('join_session_event:', join_session_event)
                    continue

                # Test for ParticipantEvent
                participant_event = messages.ParticipantEvent()
                if any_msg.Unpack(participant_event):
                    # TODO Handle participant_event
                    print('participant_event:', participant_event)
                    continue

                # Test for StopSessionEvent
                stop_session_event = messages.StopSessionEvent()
                if any_msg.Unpack(stop_session_event):
                    # TODO Handle stop_session_event
                    print('stop_session_event:', stop_session_event)
                    continue

                # Test for UserEvent
                user_event = messages.UserEvent()
                if any_msg.Unpack(user_event):
                    # TODO Handle user_event
                    print('user_event:', user_event)
                    continue

                # Test for LeaveSessionEvent
                leave_session_event = messages.LeaveSessionEvent()
                if any_msg.Unpack(leave_session_event):
                    # TODO Handle leave_session_event
                    print('leave_session_event:', leave_session_event)
                    continue

                # Test for JoinSessionReply
                join_session_reply = messages.JoinSessionReplyEvent()
                if any_msg.Unpack(join_session_reply):
                    # TODO Handle join_session_reply
                    print('join_session_reply:', join_session_reply)
                    continue

                # Unhandled message
                print('Unhandled event :', any_msg)

    except ParseError as e:
        print(e)
    return


async def main(url, token):

    async with aiohttp.ClientSession() as client:

        # Create alive publishing task
        status_task = asyncio.create_task(send_device_status(client, url + status_api_endpoint, token))

        params = {'token': token}
        login_info = await fetch(client, url + login_api_endpoint, params)
        print(login_info)
        if 'websocket_url' in login_info:
            websocket_url = login_info['websocket_url']

            ws = await client.ws_connect(url=websocket_url, ssl=False, autoping=True, autoclose=True)
            print(ws)

            while True:
                msg = await ws.receive()

                if msg.type == aiohttp.WSMsgType.text:
                    await parse_message(client, msg.json())
                if msg.type == aiohttp.WSMsgType.closed:
                    print('websocket closed')
                    break
                if msg.type == aiohttp.WSMsgType.error:
                    print('websocket error')
                    break

        print('cancel status task')
        status_task.cancel()
        await status_task
        return


if __name__ == '__main__':

    url = "https://localhost:40075"
    token = "Copy token here."

    while True:
        try:
            print('start loop')
            loop = asyncio.get_event_loop()
            main_task = asyncio.ensure_future(main(url, token))

            for signal in [SIGINT, SIGTERM]:
                loop.add_signal_handler(signal, main_task.cancel)

            loop.run_until_complete(main_task)
        except asyncio.CancelledError as e:
            print('Main Task cancelled', e)
            # Exit loop
            break
        except Exception as e:
            print(e)
            main_task.cancel()

        # Sleep few seconds and then retry...
        time.sleep(5)
