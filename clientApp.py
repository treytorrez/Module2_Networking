from pathlib import Path
from Client import Client
from typing import Any
from textual.app import App, ComposeResult
import textual.containers as txc
from textual.widgets import DirectoryTree, Footer, Header, Button, Label, Tree

directory = dict[str, 'directory | None']


HOST, PORT = "127.0.0.1", 65432

class ButtonGroup(txc.HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Button("Download", id="dl")
        yield Button("Upload", id="ul")


class ServerFileBrowser(txc.VerticalGroup):
    BORDER_SUBTITLE = "Local Files"

    def __init__(self, client: Client, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.client = client

    def compose(self) -> ComposeResult:
        yield Label("Server Files")
        tree: Tree[Any] = Tree("Server Files", id="serverfiles")
        self.build_tree(tree, Client.RetrieveDirectory(self.client))
        yield tree

    def build_tree(self, node: Tree[Any], data: directory) -> None:
        for key, value in data.items():
            if value is None:
                node.root.add_leaf(key)
            else:
                node.root.add(key)


class LocalFileBrowser(txc.VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Local Files")
        yield DirectoryTree(str(Path("./")), id="localfiles")


class ClientGUI(App[None]):
    CSS_PATH = "./clientStyles.tcss"

    def __init__(self):
        super().__init__()
        self.client = Client(host=HOST, port=PORT)
        self.sfb:ServerFileBrowser = ServerFileBrowser(client=self.client)

    def compose(self) -> ComposeResult:
        yield Header()
        yield txc.HorizontalGroup(
            self.sfb, LocalFileBrowser(), id="files"
        )
        yield ButtonGroup(id="buttons")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        localfiles: DirectoryTree = self.query_one(
            "#localfiles", expect_type=DirectoryTree
        )
        serverfiles: Tree[directory] = self.query_one("#serverfiles", expect_type=Tree)
        match event.button.id:
            case "ul":
                selected_file = localfiles.cursor_node
                if selected_file is not None and selected_file.data is not None:
                    event.button.label = f"Uploading {selected_file.label}!"
                    self.client.send_with_len("SET")
                    # The DirectoryTree provides a pathlib.Path via .data.path (usually)
                    self.client.send(Path(selected_file.data.path), file=True)
                    self.sfb.refresh(recompose=True)
            case "dl":
                selected_file = serverfiles.cursor_node
                if selected_file is not None:
                    event.button.label = f"Downloading {selected_file.label}!"
                    self.client.send_with_len("GET")
                    self.client.send(str(selected_file.label))
                    self.client.recv(file=True)
                    localfiles.compose()
                    localfiles.reload()
            case _:
                pass


if __name__ == "__main__":
    app = ClientGUI()
    app.run()
