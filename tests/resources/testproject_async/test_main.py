import asyncio
import subprocess


def test_sync_shell() -> None:
    proc = subprocess.run(
        ["./test.sh", "sync"],
        stdout=subprocess.PIPE,
    )
    assert proc.stdout == b"hello\n" and proc.returncode == 0


async def test_async_shell() -> None:
    proc = await asyncio.create_subprocess_exec(
        "./test.sh",
        "async",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    assert proc.returncode == 0 and stdout == b"hello\n"
