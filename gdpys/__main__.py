import click

@click.group(name="gdpys")
def gdpys():
    pass

@gdpys.command(name="start")
@click.option("--debug", default=False, is_flag=True)
def start(debug, local):
    __import__("main").main(debug)

if __name__ == "__main__":
    gdpys()