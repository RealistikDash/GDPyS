# CODE RESPONSIBLE FOR UPDATING DATABASES TO GDPYS
from console import Log, Fail, Success
import re
from mysql.connector import Error
from os import path

def ExecuteSQLFile(cursor, sql_file):
    """Executes an SQL file.
    
    Credit: https://stackoverflow.com/a/19159041"""
    Log(f"Executing file {sql_file}")
    statement = ""

    for line in open(sql_file):
        if re.match(r'--', line):  # ignore sql comment lines
            continue
        if not re.search(r';$', line):  # keep appending lines that don't end in ';'
            statement = statement + line
        else:  # when you get a line ending in ';' then exec statement and reset for next statement
            statement = statement + line
            #print "\n\n[DEBUG] Executing SQL statement:\n%s" % (statement)
            try:
                cursor.execute(statement)
            except Exception as e:
                Fail(f"Could now execute command! Err {e}")

            statement = ""

def ImportGDPySDatabase(cursor):
    """Imports the GDPyS MySQL database."""
    if path.exists("GDPyS.sql"):
        Log("Importing GDPyS database!")
        ExecuteSQLFile(cursor, "GDPyS.sql")
        Success("Successfully imported database!")
    else:
        Fail("SQL file is missing! Make sure GDPyS.sql exists!")
        raise FileNotFoundError
