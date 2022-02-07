import click

from tornado import web, ioloop

from .handlers import FrontendHandler, ApiHandler, RenderedHandler


@click.command()
@click.option('--basepath', default='/', help='The URL path that the authoring server is mounted at')
@click.option('--port', default=6543, help='The port the authoring server should listen on')
@click.option('--repository-location', help='The location to clone the remote repository to')
def serve(basepath, port, repository_location):
    """Run the authoring server."""
    if repository_location.endswith('/'):
        repository_location = repository_location[:-1]
    app = web.Application([
        (basepath, web.RedirectHandler, {'url': f'{basepath}app'}),
        (f'{basepath}app(.*)', FrontendHandler, {'basepath': basepath}),
        (f'{basepath}api', ApiHandler, {'repository_location': repository_location}),
        (f'{basepath}rendered(.*)', RenderedHandler, {'repository_location': repository_location})
    ], debug=True)
    app.listen(address='127.0.0.1',
               port=port)
    ioloop.IOLoop.current().start()


serve()
