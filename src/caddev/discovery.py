"""Discover and connect to the running FreeCAD bridge."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

from .log import error, info, success, warning
from .rpc import PROTOCOL_VERSION, RpcClient, RpcError


DEFAULT_RETRIES = 5
DEFAULT_RETRY_DELAY = 1.0


@dataclass(frozen=True)
class BridgeInfo:
    host: str
    port: int
    token: str
    protocol: int


def discovery_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    else:
        base = Path(
            os.environ.get(
                "XDG_CACHE_HOME",
                Path.home() / ".cache",
            )
        )

    return base / "codecad" / "bridge.json"


def read_bridge_info() -> BridgeInfo:
    path = discovery_path()

    if not path.exists():
        raise RuntimeError(
            f"FreeCAD bridge discovery file not found: {path}"
        )

    try:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"could not read FreeCAD bridge discovery file: {path}"
        ) from exc

    try:
        info = BridgeInfo(
            host=str(data["host"]),
            port=int(data["port"]),
            token=str(data["token"]),
            protocol=int(data["protocol"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(
            "invalid FreeCAD bridge discovery file"
        ) from exc

    if info.protocol != PROTOCOL_VERSION:
        raise RuntimeError(
            f"bridge protocol mismatch: "
            f"caddev={PROTOCOL_VERSION}, "
            f"FreeCAD={info.protocol}"
        )

    return info


def connect_freecad(
    *,
    retries: int = DEFAULT_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
) -> RpcClient:
    info("Finding FreeCAD bridge...")

    bridge = read_bridge_info()

    info(
        f"Bridge advertised at "
        f"{bridge.host}:{bridge.port}"
    )

    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        client = RpcClient(
            host=bridge.host,
            port=bridge.port,
            token=bridge.token,
            timeout=5.0,
        )

        try:
            client.connect()

            hello = client.call(
                "bridge.hello",
                rpc_timeout=5.0,
            )

            success(
                f"Connected to FreeCAD "
                f"at {bridge.host}:{bridge.port}"
            )

            return client

        except (OSError, RpcError) as exc:
            last_error = exc
            client.close()

            if attempt == retries:
                break

            warning(
                f"Connection failed "
                f"({attempt}/{retries}); "
                f"retrying in {retry_delay:.1f}s"
            )

            time.sleep(retry_delay)

    raise RuntimeError(
        f"could not connect to FreeCAD bridge at "
        f"{bridge.host}:{bridge.port} "
        f"after {retries} attempts"
    ) from last_error
