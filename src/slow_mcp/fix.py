import asyncio
import os

from mcp.server.fastmcp import Context

from .mcp import mcp

__all__ = ["fix_violation"]


async def report_progress(
    ctx: Context, start_time: float, poll_interval: int, stop_event: asyncio.Event
):
    """
    Reports numeric progress (elapsed time) periodically until stop_event is set.
    """
    try:
        while not stop_event.is_set():
            elapsed = asyncio.get_running_loop().time() - start_time
            if ctx:
                await ctx.report_progress(elapsed)
            await asyncio.sleep(poll_interval)
    except asyncio.CancelledError:
        # Task was cancelled intentionally.
        pass


@mcp.tool()
async def fix_violation(timeout: int = 300, ctx: Context = None) -> str:
    """Fix a violation using the fix agent."""

    try:
        # Start the shell command process.
        command = f"{os.path.dirname(os.path.abspath(__file__))}/slow.sh"

        # Check if the command script exists.
        if not os.path.exists(command):
            return f"Error: Script not found: {command}"

        # Check if the script is executable.
        if not os.access(command, os.X_OK):
            return (
                f"Error: Script is not executable: {command}. "
                f"To make it executable, run: chmod +x {command}"
            )

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        start_time = asyncio.get_running_loop().time()
        poll_interval = 5  # seconds
        stop_event = asyncio.Event()

        # Create a task to wait for process completion.
        command_task = asyncio.create_task(process.communicate())
        # Create a task to report progress periodically.
        progress_task = asyncio.create_task(
            report_progress(ctx, start_time, poll_interval, stop_event)
        )

        # Wait for the command_task to finish within the given timeout.
        done, pending = await asyncio.wait({command_task}, timeout=timeout)

        if not command_task.done():
            # The command did not finish in time.
            process.kill()
            # Await process termination.
            stdout, stderr = await process.communicate()
            stop_event.set()
            progress_task.cancel()
            return f"Command exceeded timeout of {timeout} seconds."
        else:
            # Command completed in time.
            stdout, stderr = await command_task
            stop_event.set()
            progress_task.cancel()
            output = (stdout.decode() if stdout else "") + (stderr.decode() if stderr else "")
            return output

    except Exception as e:
        # Cancel timer if it was started.
        if "stop_event" in locals():
            stop_event.set()
        if "progress_task" in locals():
            progress_task.cancel()
        return f"Command execution failed: {e}"
