from datetime import datetime
from typing import Tuple

import aioipfs
import torch
from torch import nn


# TODO: switch to sync ipfs framework?


async def save_model_ipfs(
    state_dict: nn.Module.state_dict, ipfs_host: str
) -> Tuple[str, str]:
    client = aioipfs.AsyncIPFS(maddr=ipfs_host)
    cur_time = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".pt")
    torch.save(state_dict, f"upload/{cur_time}")
    [cids] = [entry["Hash"] async for entry in client.add(f"upload/{cur_time}")]
    cids = str(cids)
    await client.close()
    return cids


async def load_model_ipfs(cid: str, ipfs_host: str) -> nn.Module.state_dict:
    client = aioipfs.AsyncIPFS(maddr=ipfs_host)
    await client.get(path=cid, dstdir="download")
    await client.close()
    return torch.load(f"download/{cid}")
