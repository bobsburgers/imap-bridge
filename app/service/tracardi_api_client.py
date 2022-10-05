from aiohttp import ClientResponse
from typing import Tuple, Any

import json

import aiohttp


class TracardiApiClient:

    def __init__(self, host):
        self.token = None
        self.api_host = host

    def _host(self, path):
        return "{}{}".format(self.api_host, path)

    async def set_credentials(self, username: str = None, password: str = None):
        self.token = await self._authorize(username, password)

    async def _authorize(self, username: str, password: str):
        response, json, data = await self.post(
            '/user/token',
            data={
                "username": username,
                "password": password
            }
        )

        if response.status == 200:
            token = "{} {}".format(json['token_type'], json['access_token'])
            return token
        else:
            raise ConnectionError(f"Tracardi connection error status {response.status}. Details: {data}")

    async def request(self, endpoint, json=None, data=None, params=None, method='POST'):
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method,
                    self._host(endpoint),
                    json=json,
                    data=data,
                    params=params,
                    timeout=180,
                    headers={"Authorization": self.token} if self.token else None
            ) as response:
                return response, await response.json(), await response.text()

    async def post(self, endpoint, json=None, data=None, params=None) -> Tuple[ClientResponse, Any, str]:
        return await self.request(endpoint, json=json, data=data, params=params, method="post")

    async def get(self, endpoint, params=None):
        return await self.request(endpoint, params=params, method="get")

    async def delete(self, endpoint, json=None, data=None, params=None):
        return await self.request(endpoint, json, data=data, params=params, method="delete")

    async def put(self, endpoint, json=None, data=None, params=None):
        return await self.request(endpoint, json, data=data, params=params, method="put")
