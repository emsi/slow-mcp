from enum import Enum

import typer


app = typer.Typer()


class Mode(str, Enum):
    stdio = "stdio"
    sse = "sse"

    def __str__(self):
        return self.value


@app.command()
def main(
    context: typer.Context,
    transport: Mode = typer.Option(
        Mode.sse,
        help="Transport method for communication. 'stdio' for standard input/output, 'sse' for server-sent events.",
    ),
    port: int = typer.Option(
        3001,
        help="Port number for the server. Default is 3001.",
    ),
):
    # This is the main entry point of the application.
    # It is called when the application is run from the command line.
    # It initializes the MCP and runs it.
    from . import mcp
    mcp.mcp = mcp.FastMCP("Violations manager", port=port)
    from .fix import slow_mcp
    mcp.mcp.run(transport=transport)


def start():
    app()


if __name__ == "__main__":
    app()
