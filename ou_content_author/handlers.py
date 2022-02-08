import asyncio
import functools
import json
import os
import subprocess

from git import Repo, Actor
from importlib import resources
from mimetypes import guess_type
from shutil import rmtree
from tornado import web, websocket


async def render(basepath: str):
    """Render the project at the given basepath."""
    install = await asyncio.create_subprocess_exec('poetry', 'install', cwd=basepath)
    await install.wait()
    build = await asyncio.create_subprocess_exec('poetry', 'run', 'make', 'html', cwd=basepath, stdout=subprocess.PIPE)
    await build.wait()
    return (await build.stdout.read()).decode('utf-8')


class FrontendHandler(web.RequestHandler):
    """Handles serving the UI."""

    def initialize(self, basepath: str):
        self.basepath = basepath

    def get(self, path):
        """Return the UI resource at ``path``."""
        if path.startswith('/'):
            path = path[1:]
        base = resources.files('ou_content_author') / 'frontend' / 'public'
        try:
            self.send_resource(base, path.split('/'))
        except FileNotFoundError:
            self.send_resource(base, ('index.html',))

    def send_resource(self, resource, path):
        """Send the resource identified by the ``path``.

        Performs content modification when sending the index.html file to set the correct base path for all resources.
        """
        for part in path:
            resource = resource / part
        try:
            mimetype = guess_type(path[-1])
            if mimetype and mimetype[0]:
                self.set_header('Content-Type', mimetype[0])
            if path == ('index.html',):
                content = resource.read_bytes().decode('utf-8')
                content = content.replace('{app_path}', f'{self.basepath}app/')
                self.write(content.encode('utf-8'))
            else:
                self.write(resource.read_bytes())
        except IsADirectoryError:
            raise FileNotFoundError
        except IndexError:
            raise FileNotFoundError


class ApiHandler(websocket.WebSocketHandler):

    def initialize(self, repository_location: str):
        self._repository_location = repository_location
        self._task = None

    async def on_message(self, message: str):
        data = json.loads(message)
        if 'type' in data:
            if data['type'] == 'clone-repository':
                self.clone_repository(data)
            elif data['type'] == 'delete-repository':
                self.delete_repository(data)
            elif data['type'] == 'checkout-branch':
                self.checkout_branch(data)
            elif data['type'] == 'select-block':
                self.select_block(data)
            elif data['type'] == 'load-file-content':
                await self.load_file_content(data)
            elif data['type'] == 'save-file-content':
                await self.save_file_content(data)
            elif data['type'] == 'commit-changes':
                self.commit_changes(data)
            elif data['type'] == 'discard-changes':
                self.discard_changes(data)
            elif data['type'] == 'add-file':
                self.add_file(data)
            elif data['type'] == 'delete-file':
                self.delete_file(data)

    def send_message(self, message: dict):
        self.write_message(json.dumps(message))

    def clone_repository(self, data: dict):
        """Clone the repository at the URL."""
        if 'url' in data:
            if os.path.exists(self._repository_location):
                rmtree(self._repository_location)
            repo = Repo.clone_from(data['url'], self._repository_location)
            branches = [ref.path.split('/')[-1] for ref in repo.remote().refs if not ref.path.endswith('/HEAD')]
            self.send_message({
                'type': 'repository',
                'branches': branches
            })

    def delete_repository(self, data: dict):
        if os.path.exists(self._repository_location):
            rmtree(self._repository_location)
        self.send_message({
            'type': 'repository-deleted',
        })

    def checkout_branch(self, data: dict):
        """Checkout the branch either locally or from remote"""
        if 'branch' in data:
            repo = Repo(self._repository_location)
            found = False
            for ref in repo.branches:
                if ref.path.endswith(f'/{data["branch"]}'):
                    ref.checkout()
                    found = True
                    break
            if not found:
                for ref in repo.remote().refs:
                    if ref.path.endswith(f'/{data["branch"]}'):
                        repo.git.checkout('-b', data['branch'], ref.path)
                        found = True
            if found:
                blocks = []
                for basepath, dirnames, filenames in os.walk(self._repository_location):
                    for filename in filenames:
                        if filename == 'conf.py':
                            blocks.append(os.path.join(basepath, filename)[len(self._repository_location):])
                self.send_message({
                    'type': 'branch',
                    'blocks': blocks
                })

    def select_block(self, data: dict):
        """Select a given block."""
        if 'block' in data:
            self.scan_block(data['block'])

    async def load_file_content(self, data: dict):
        """Load the content of a file."""
        if 'file' in data and 'block' in data and 'directory' in data['file'] and 'filename' in data['file']:
            filepath = os.path.join(self._repository_location,
                                    os.path.dirname(data['block'])[1:],
                                    data['file']['directory'],
                                    data['file']['filename'])
            if os.path.exists(filepath) and os.path.abspath(filepath).startswith(os.path.abspath(self._repository_location)):
                with open(filepath) as in_f:
                    self.send_message({
                        'type': 'file-content',
                        'content': in_f.read()
                    })
                await self.run_render(os.path.join(self._repository_location, os.path.dirname(data['block'])[1:]),
                                      os.path.dirname(data['block'])[1:],
                                      os.path.join(data['file']['directory'], data['file']['filename']))

    async def save_file_content(self, data: dict):
        """Save the updated file content."""
        if 'file' in data and 'block' in data and 'directory' in data['file'] and 'filename' in data['file'] and 'content' in data:
            filepath = os.path.join(self._repository_location,
                                    os.path.dirname(data['block'])[1:],
                                    data['file']['directory'],
                                    data['file']['filename'])
            if os.path.exists(filepath) and os.path.abspath(filepath).startswith(os.path.abspath(self._repository_location)):
                with open(filepath, 'w') as out_f:
                    out_f.write(data['content'])
                await self.run_render(os.path.join(self._repository_location, os.path.dirname(data['block'])[1:]),
                                      os.path.dirname(data['block'])[1:],
                                      os.path.join(data['file']['directory'], data['file']['filename']))
            self.check_repo_changes()


    def commit_changes(self, data: dict):
        """Commit and push changes."""
        if 'name' in data and data['name'] and 'email' in data and data['email'] and 'message' in data and data['message']:
            repo = Repo(self._repository_location)
            if len(repo.index.diff(None) + repo.index.diff('HEAD')) > 0 or len(repo.untracked_files) > 0:
                repo.git.add('.')
                actor = Actor(data['name'], data['email'])
                repo.index.commit(data['message'], author=actor, committer=actor)
                repo.git.push('--force')
            self.send_message({
                'type': 'changes-committed',
            })
            self.check_repo_changes()

    def discard_changes(self, data: dict):
        """Discard any changes."""
        repo = Repo(self._repository_location)
        repo.git.checkout('--', '.')
        self.send_message({
            'type': 'changes-discarded',
        })
        self.check_repo_changes()

    def add_file(self, data: dict):
        if 'block' in data and 'file' in data and 'directory' in data['file'] and 'filename' in data['file']:
            filepath = os.path.join(self._repository_location,
                                    os.path.dirname(data['block'])[1:],
                                    data['file']['directory'],
                                    data['file']['filename'])
            if not os.path.exists(filepath) and os.path.abspath(filepath).startswith(os.path.abspath(self._repository_location)):
                if not os.path.exists(os.path.dirname(filepath)):
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w') as out_f:
                    if filepath.endswith('.md'):
                        out_f.write('# Page Title')
            self.scan_block(data['block'])
            self.check_repo_changes()

    def delete_file(self, data: dict):
        if 'block' in data and 'file' in data and 'directory' in data['file'] and 'filename' in data['file']:
            filepath = os.path.join(self._repository_location,
                                    os.path.dirname(data['block'])[1:],
                                    data['file']['directory'],
                                    data['file']['filename'])
            if os.path.exists(filepath) and os.path.abspath(filepath).startswith(os.path.abspath(self._repository_location)):
                os.unlink(filepath)
            self.scan_block(data['block'])
            self.check_repo_changes()

    async def run_render(self, basepath: str, block: str, filepath: str):
        """Run the render process and send the required messages."""
        if basepath.endswith('/source'):
            basepath = basepath[:-7]
        self.send_message({
            'type': 'file-rendering',
        })
        if self._task is not None and not self._task.done():
            self._task.cancel()
        self._task = asyncio.create_task(render(basepath))
        self._task.add_done_callback(functools.partial(self.render_complete, block, filepath))

    def render_complete(self, block: str, filepath: str, task: asyncio.Task):
        """Report rendering completed to the client."""
        if not task.cancelled():
            result = task.result()
            if result:
                if '.' in filepath:
                    filepath = f'{filepath[:filepath.rfind(".")]}.html'
                else:
                    filepath = f'{filepath}.html'
                if block.endswith('/source'):
                    block = block[:-7]
                self.send_message({
                    'type': 'file-rendered',
                    'url': f'/{block}/{filepath}',
                    'output': result,
                })

    def check_repo_changes(self):
        """Check if there are changes to commit in the repo."""
        repo = Repo(self._repository_location)
        if len(repo.index.diff(None) + repo.index.diff('HEAD')) > 0 or len(repo.untracked_files) > 0:
            self.send_message({
                'type': 'changes-found'
            })
        else:
            self.send_message({
                'type': 'no-changes-found'
            })

    def scan_block(self, block):
        """Scan the block and send back the """
        blockpath = os.path.dirname(f'{self._repository_location}{block}')
        files = []
        for basepath, dirnames, filenames in os.walk(blockpath):
            for filename in filenames:
                if filename.endswith('.md'):
                    files.append({
                        'directory': basepath[len(blockpath) + 1:],
                        'filename': filename
                    })
        self.send_message({
            'type': 'block',
            'path': block,
            'files': files
        })


class RenderedHandler(web.RequestHandler):
    """Handler for the rendered HTML pages."""

    def initialize(self, repository_location: str):
        """Initialise the handler."""
        self._repository_location = repository_location

    def get(self, path: str):
        """Get the rendered HTML page."""
        if path.startswith('/'):
            path = path[1:]
        path_elements = path.split('/')
        filepath = os.path.abspath(os.path.join(self._repository_location,
                                                path_elements[0],
                                                'build',
                                                'html',
                                                *path_elements[1:]))
        if filepath.startswith(self._repository_location) and os.path.exists(filepath):
            mimetype = guess_type(filepath)
            if mimetype and mimetype[0]:
                self.set_header('Content-Type', mimetype[0])
            with open(filepath, 'rb') as in_f:
                self.write(in_f.read())
