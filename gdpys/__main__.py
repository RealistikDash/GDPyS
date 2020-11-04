import click, asyncio
from outdated import warn_if_outdated
from constants import version

@click.group(name="gdpys")
def gdpys():
    warn_if_outdated("gdpys", version)

@gdpys.command(name="start")
@click.option("--debug", default=False, is_flag=True)
def start(debug):
    __import__("main").main(debug) # hacky but works

@gdpys.command(name="cron")
def cron():
    cron = __import__("cron.cron").cron
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cron.run_cron())
    

if __name__ == "__main__":
    gdpys()