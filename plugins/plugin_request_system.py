import aiohttp
from typing import Optional, Dict, Any
import numpy as np

class PluginRequestSystem:
    def __init__(self, developer_api_url: str):
        self.developer_api_url = developer_api_url

    async def request_plugin(self, query_vector: Optional[np.ndarray], request_description: str) -> Optional[Dict[str, Any]]:
        if query_vector is None:
            print("Error: query_vector is None. Unable to request plugin.")
            return None

        async with aiohttp.ClientSession() as session:
            payload = {
                "query_vector": query_vector.tolist(),
                "description": request_description
            }
            try:
                async with session.post(f"{self.developer_api_url}/request_plugin", json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Failed to request plugin: HTTP {response.status}")
                        return None
            except aiohttp.ClientError as e:
                print(f"Network error when requesting plugin: {e}")
                return None