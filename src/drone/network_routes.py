from dataclasses import dataclass
import os
import socket
from typing import Optional, Tuple

import requests
from requests.adapters import HTTPAdapter


def _env_optional(name: str) -> Optional[str]:
    value = os.getenv(name)
    if value is None:
        return None

    value = value.strip()
    return value or None


def _env_int(name: str, default: int) -> int:
    value = _env_optional(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {value!r}") from exc


@dataclass(frozen=True)
class TelloNetworkConfig:
    host: str
    command_port: int
    local_ip: Optional[str]
    local_port: int
    state_port: int
    video_host: str
    video_port: int
    video_url_override: Optional[str]

    @property
    def command_address(self) -> Tuple[str, int]:
        return (self.host, self.command_port)

    @property
    def bind_address(self) -> Tuple[str, int]:
        return (self.local_ip or "", self.local_port)

    @property
    def public_bind_address(self) -> Tuple[str, int]:
        return (self.local_ip or "0.0.0.0", self.local_port)

    @property
    def video_url(self) -> str:
        if self.video_url_override:
            return self.video_url_override

        return f"udp://@{self.video_host}:{self.video_port}"


def load_tello_config() -> TelloNetworkConfig:
    return TelloNetworkConfig(
        host=os.getenv("TELLO_HOST", "192.168.10.1"),
        command_port=_env_int("TELLO_COMMAND_PORT", 8889),
        local_ip=_env_optional("TELLO_LOCAL_IP"),
        local_port=_env_int("TELLO_LOCAL_PORT", 9000),
        state_port=_env_int("TELLO_STATE_PORT", 8890),
        video_host=os.getenv("TELLO_VIDEO_HOST", "0.0.0.0"),
        video_port=_env_int("TELLO_VIDEO_PORT", 11111),
        video_url_override=_env_optional("TELLO_VIDEO_URL"),
    )


def bind_tello_socket(sock: socket.socket, config: Optional[TelloNetworkConfig] = None) -> Tuple[str, int]:
    config = config or load_tello_config()

    # On Windows, SO_REUSEADDR can let two local processes bind the same UDP
    # port and make delivery ambiguous. The Tello CLI must own its command port.
    if os.name == "nt" and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    else:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(config.bind_address)
    return config.public_bind_address


def get_api_source_ip() -> Optional[str]:
    return _env_optional("PIER_API_SOURCE_IP") or _env_optional("API_SOURCE_IP")


class SourceAddressHTTPAdapter(HTTPAdapter):
    def __init__(self, source_ip: str, *args, **kwargs):
        self.source_ip = source_ip
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        pool_kwargs["source_address"] = (self.source_ip, 0)
        return super().init_poolmanager(
            connections,
            maxsize,
            block=block,
            **pool_kwargs,
        )

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        proxy_kwargs["source_address"] = (self.source_ip, 0)
        return super().proxy_manager_for(proxy, **proxy_kwargs)


def create_api_session(source_ip: Optional[str] = None) -> requests.Session:
    session = requests.Session()
    selected_source_ip = source_ip or get_api_source_ip()

    if selected_source_ip:
        adapter = SourceAddressHTTPAdapter(selected_source_ip)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

    return session


def describe_network_plan(tello_config: Optional[TelloNetworkConfig] = None) -> str:
    tello_config = tello_config or load_tello_config()
    api_source_ip = get_api_source_ip() or "rota default do sistema operacional"

    return "\n".join(
        [
            "Plano de rede ativo:",
            (
                "  - Tello/local UDP: "
                f"{tello_config.public_bind_address[0]}:{tello_config.local_port} -> "
                f"{tello_config.host}:{tello_config.command_port}"
            ),
            f"  - Video Tello: {tello_config.video_url}",
            f"  - Estado Tello: UDP {tello_config.state_port}",
            f"  - APIs/Internet: {api_source_ip}",
        ]
    )
