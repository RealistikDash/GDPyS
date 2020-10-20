import click, asyncio

@click.group(name="gdpys")
def gdpys():
    pass

@gdpys.command(name="start")
@click.option("--debug", default=False, is_flag=True)
def start(debug):
    __import__("main").main(debug) # hacky but works

@gdpys.command(name="cron")
def cron():
    #click.echo("Not implemented yet.");return
    cron = __import__("cron.cron").cron
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cron.run_cron())
    

if __name__ == "__main__":
    gdpys()