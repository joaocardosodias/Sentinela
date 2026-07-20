import argparse
import select
import socket
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class UdpStats:
    name: str
    packets: int = 0
    total_bytes: int = 0
    first_address: Optional[tuple[str, int]] = None


def bind_udp_listener(host: str, port: int, name: str, exclusive: bool) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if exclusive and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    elif not exclusive:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)

    try:
        sock.bind((host, port))
    except OSError as exc:
        sock.close()
        raise SystemExit(
            f"ERRO_BIND {name} {host or '0.0.0.0'}:{port}: {exc}. "
            "Feche processos antigos da CLI/probe do Tello e tente novamente."
        ) from exc

    sock.setblocking(False)
    return sock


def send_and_wait(sock: socket.socket, tello_address, command: str, timeout: float) -> bytes:
    print(f"> {command}")
    sock.sendto(command.encode("ascii"), tello_address)
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        readable, _, _ = select.select([sock], [], [], 0.2)
        if not readable:
            continue

        data, address = sock.recvfrom(2048)
        print(f"< {address}: {data.decode('utf-8', errors='replace')}")
        return data

    if timeout > 0:
        print(f"< timeout esperando resposta de {command}")
    return b""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe de video UDP do DJI Tello sem depender do OpenCV.",
    )
    parser.add_argument("--tello-host", default="192.168.10.1")
    parser.add_argument("--command-port", type=int, default=8889)
    parser.add_argument("--local-command-port", type=int, default=9000)
    parser.add_argument("--state-port", type=int, default=8890)
    parser.add_argument("--extra-port", type=int, default=8899)
    parser.add_argument("--listen-host", default="")
    parser.add_argument("--video-port", type=int, default=11111)
    parser.add_argument("--seconds", type=float, default=15)
    parser.add_argument(
        "--reuse-address",
        action="store_true",
        help="Usa SO_REUSEADDR em vez de bind exclusivo. Use apenas para depuracao.",
    )
    parser.add_argument(
        "--no-streamoff-before",
        action="store_true",
        help="Nao envia streamoff antes do streamon.",
    )
    args = parser.parse_args()

    tello_address = (args.tello_host, args.command_port)
    exclusive = not args.reuse_address

    command_socket = bind_udp_listener(
        args.listen_host,
        args.local_command_port,
        "command",
        exclusive=exclusive,
    )
    video_socket = bind_udp_listener(
        args.listen_host,
        args.video_port,
        "video",
        exclusive=exclusive,
    )
    state_socket = bind_udp_listener(
        args.listen_host,
        args.state_port,
        "state",
        exclusive=exclusive,
    )
    extra_socket = bind_udp_listener(
        args.listen_host,
        args.extra_port,
        "extra",
        exclusive=exclusive,
    )

    sockets = {
        video_socket: UdpStats(name=f"video:{args.video_port}"),
        state_socket: UdpStats(name=f"state:{args.state_port}"),
        extra_socket: UdpStats(name=f"extra:{args.extra_port}"),
    }

    bind_host = args.listen_host or "0.0.0.0"
    mode = "exclusivo" if exclusive else "SO_REUSEADDR"
    print(
        "Escutando UDP antes do streamon "
        f"em {bind_host}:{args.video_port}, {bind_host}:{args.state_port}, "
        f"{bind_host}:{args.extra_port} ({mode})"
    )

    command_mode_enabled = False

    try:
        command_response = send_and_wait(command_socket, tello_address, "command", timeout=5)
        if not command_response:
            return 3
        command_mode_enabled = True

        if not args.no_streamoff_before:
            send_and_wait(command_socket, tello_address, "streamoff", timeout=3)
            time.sleep(1)

        streamon_response = send_and_wait(command_socket, tello_address, "streamon", timeout=5)
        if not streamon_response:
            return 4

        deadline = time.monotonic() + args.seconds
        while time.monotonic() < deadline:
            readable, _, _ = select.select(list(sockets), [], [], 0.5)
            if not readable:
                continue

            for sock in readable:
                data, address = sock.recvfrom(65535)
                stats = sockets[sock]
                stats.packets += 1
                stats.total_bytes += len(data)
                stats.first_address = stats.first_address or address

                if stats.packets <= 5:
                    print(
                        f"{stats.name} packet {stats.packets}: "
                        f"{len(data)} bytes from {address} head={data[:16].hex()}"
                    )

        for stats in sockets.values():
            print(
                "UDP_SUMMARY "
                f"{stats.name} packets={stats.packets} "
                f"bytes={stats.total_bytes} first_addr={stats.first_address}"
            )
    finally:
        if command_mode_enabled:
            send_and_wait(command_socket, tello_address, "streamoff", timeout=2)
        for sock in [command_socket, video_socket, state_socket, extra_socket]:
            sock.close()

    return 0 if sockets[video_socket].packets > 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
