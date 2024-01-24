import asyncio
from datetime import datetime
from typing import List, Tuple
import torch

import aioipfs
from flwr.common.typing import NDArray, Parameters
import pickle

import async_timeout

# TODO: switch to sync ipfs framework?


async def save_model_ipfs(state_dict, ipfs_host: str) -> str:
    client = aioipfs.AsyncIPFS(maddr=ipfs_host)
    cur_time = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".pickle")
    # print(type(state_dict))
    torch.save(state_dict, f"upload/{cur_time}")
    # np.save(f"upload/{cur_time}", state_dict, allow_pickle=True)
    # pickle.dump(state_dict, open(f"upload/{cur_time}", "wb"))
    [cid] = [entry["Hash"] async for entry in client.add(f"upload/{cur_time}")]
    cid = str(cid)
    await client.close()
    return cid


async def load_model_ipfs(cid: str, ipfs_host: str):
    client = aioipfs.AsyncIPFS(maddr=ipfs_host)
    async with async_timeout.timeout(10):
        await client.get(path=cid, dstdir="download")
    await client.close()
    return torch.load(f"download/{cid}")
    # return np.load(f"download/{cid}", allow_pickle=True)
    # return pickle.load(open(f"download/{cid}", "rb"))


async def load_models(cid_list: List[str], ipfs_host: str) -> List:
    return await asyncio.gather(*[load_model_ipfs(cid, ipfs_host) for cid in cid_list])
