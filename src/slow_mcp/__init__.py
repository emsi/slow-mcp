from enum import Enum


import typer


from .fix import *
from .mcp import mcp


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
):
    # This is the main entry point of the application.
    # It is called when the application is run from the command line.
    # It initializes the MCP and runs it.
    mcp.run(transport=transport)


def start():
    app()


if __name__ == "__main__":
    app()
