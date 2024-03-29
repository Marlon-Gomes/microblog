# Imports from standard libraries
import os, click

# Register the current app
def register(app):
    @app.cli.group()
    def translate():
        """ Translation and localization commands."""
        pass

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """ Initialize a new language."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot  .'):
            raise RuntimeError('Extract command failed.')
        if os.system(
            'pybabel init -i messages.pot -d app/translations -l ' + lang):
            raise RuntimeError('Initialization command failed')

    @translate.command()
    def update():
        """ Update all languages."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot  .'):
            raise RuntimeError('Extract command failed.')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('Update command failed.')

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('Compile command failed.')
