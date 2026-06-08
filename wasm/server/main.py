"""OmniLaTeX WebSocket Compilation Server.

Wraps buildlib to accept LaTeX source via WebSocket, compile it,
and stream back logs + the resulting PDF.

Usage:
    python wasm/server/main.py [--port 8765] [--host localhost]

Protocol:
    Client -> Server: {"type": "compile", "source": "...", "doctype": "article"}
    Server -> Client: {"type": "log", "line": "..."}
    Server -> Client: {"type": "success", "pdf": "<base64>"}
    Server -> Client: {"type": "error", "message": "..."}
    Server -> Client: {"type": "progress", "message": "..."}
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("omnilatex-ws")

# Try to import websockets; fall back gracefully
try:
    import websockets
    import websockets.server

    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# Import buildlib for compilation
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
import sys

sys.path.insert(0, str(REPO_ROOT))

from buildlib.config import (
    INTERACTION_NONSTOP,
    LATEXMK_COMMAND,
    MAIN_TEX_FILENAME,
    ProjectConfig,
)
from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput


class CompilationServer:
    """WebSocket server that compiles LaTeX documents."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.ui = TerminalOutput(use_color=False)
        self.runner = CommandRunner(ui=self.ui, build_mode="dev", verbose=True)

    async def handle_client(self, websocket):
        """Handle a single WebSocket client connection."""
        logger.info(f"Client connected: {websocket.remote_address}")

        try:
            async for message in websocket:
                try:
                    msg = json.loads(message)
                except json.JSONDecodeError:
                    await self._send_error(websocket, "Invalid JSON")
                    continue

                if msg.get("type") == "compile":
                    await self._handle_compile(websocket, msg)
                elif msg.get("type") == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
                else:
                    await self._send_error(
                        websocket, f"Unknown message type: {msg.get('type')}"
                    )
        except Exception as exc:
            logger.error(f"Client error: {exc}")
        finally:
            logger.info(f"Client disconnected: {websocket.remote_address}")

    async def _handle_compile(self, websocket, msg: dict):
        """Compile a LaTeX document and send back the result."""
        source = msg.get("source", "")
        doctype = msg.get("doctype", "article")

        if not source.strip():
            await self._send_error(websocket, "Empty source")
            return

        await self._send_progress(websocket, f"Compiling {doctype} document...")

        # Create temporary build directory
        with tempfile.TemporaryDirectory(prefix="omnilatex-ws-") as tmpdir:
            work_dir = Path(tmpdir)

            # Write the source file
            tex_file = work_dir / MAIN_TEX_FILENAME
            tex_file.write_text(source, encoding="utf-8")

            # Create symlink to repo's config/lib directories
            for d in ("config", "lib", "lua", "bib", "assets"):
                src = self.repo_root / d
                if src.exists():
                    (work_dir / d).symlink_to(src)

            # Create symlink to omnilatex.cls
            cls_src = self.repo_root / "omnilatex.cls"
            if cls_src.exists():
                (work_dir / "omnilatex.cls").symlink_to(cls_src)

            # Compile
            await self._send_progress(websocket, "Running lualatex...")

            cmd = [
                LATEXMK_COMMAND,
                INTERACTION_NONSTOP,
                "-f",
                "-lualatex",
                MAIN_TEX_FILENAME,
            ]

            env = os.environ.copy()
            env["BUILD_MODE"] = "dev"
            env["OMNILATEX_SHELL_ESCAPE"] = "0"

            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=str(work_dir),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    env=env,
                )

                # Stream logs
                async for line in process.stdout:
                    decoded = line.decode("utf-8", errors="replace").rstrip()
                    if decoded:
                        await self._send_log(websocket, decoded)

                await process.wait()

            except FileNotFoundError:
                await self._send_error(
                    websocket, "latexmk not found. Install TeX Live."
                )
                return
            except Exception as exc:
                await self._send_error(websocket, f"Compilation error: {exc}")
                return

            # Check for PDF
            pdf_file = work_dir / f"{tex_file.stem}.pdf"
            if pdf_file.exists():
                pdf_bytes = pdf_file.read_bytes()
                pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")
                await websocket.send(
                    json.dumps({"type": "success", "pdf": pdf_b64})
                )
                await self._send_progress(
                    websocket, f"PDF generated ({len(pdf_bytes)} bytes)"
                )
            else:
                await self._send_error(
                    websocket, "PDF not generated. Check the log for errors."
                )

    async def _send_log(self, websocket, line: str):
        await websocket.send(json.dumps({"type": "log", "line": line}))

    async def _send_error(self, websocket, message: str):
        await websocket.send(json.dumps({"type": "error", "message": message}))

    async def _send_progress(self, websocket, message: str):
        await websocket.send(json.dumps({"type": "progress", "message": message}))


async def main():
    parser = argparse.ArgumentParser(description="OmniLaTeX WebSocket server")
    parser.add_argument("--host", default="localhost", help="Bind host")
    parser.add_argument("--port", type=int, default=8765, help="Bind port")
    args = parser.parse_args()

    if not HAS_WEBSOCKETS:
        print("ERROR: 'websockets' package not installed.")
        print("Install: pip install websockets")
        sys.exit(1)

    server = CompilationServer(REPO_ROOT)

    logger.info(f"Starting OmniLaTeX compilation server on {args.host}:{args.port}")
    logger.info(f"Repository root: {REPO_ROOT}")

    async with websockets.serve(server.handle_client, args.host, args.port):
        logger.info("Server running. Press Ctrl+C to stop.")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
