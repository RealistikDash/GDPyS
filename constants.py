class XorKeys():
    password = 37526
    chk = 19847
    level_password = 26364
    quests = 19847
    chests = 59182

class Permissions():
    authenticate = 2<<0
    upload_level = 2<<1
    post_comment = 2<<2
    post_acc_comment = 2<<3
    mod_regular = 2<<6
    mod_elder = 2<<7
    mod_rate = 2<<8

class Secrets():
    """All the GeometryDash secret values"""
    normal = "Wmfd2893gb7"

class ResponseCodes():
    """All the web response codes."""
    generic_fail = "-1"
    generic_success = "1"
    generic_fail2 = "-2"
    login_contact_rob = "-12"
    empty_list = "#0:0:0"

class Colours():
    """ALL THE COLOURS IN THE SKY"""
    reset = u"\u001b[0m"
    red = u"\u001b[31m"
    black = u"\u001b[30m"
    green = u"\u001b[32m"
    yellow = u"\u001b[33m"
    blue = u"\u001b[34m"
    magenta = u"\u001b[35m"
    cyan = u"\u001b[36m"
    white = u"\u001b[37m"
    all_col = [red, green, yellow, blue, magenta, cyan, white]

ASCII_ART = r"""
{col1}          _____          {col2}          _____          {col3}          _____          {col4}      _____          {col5}          _____            {reset}      
{col1}         /\    \         {col2}         /\    \         {col3}         /\    \         {col4}     |\    \         {col5}         /\    \           {reset}      
{col1}        /::\    \        {col2}        /::\    \        {col3}        /::\    \        {col4}     |:\____\        {col5}        /::\    \          {reset}      
{col1}       /::::\    \       {col2}       /::::\    \       {col3}       /::::\    \       {col4}     |::|   |        {col5}       /::::\    \         {reset}      
{col1}      /::::::\    \      {col2}      /::::::\    \      {col3}      /::::::\    \      {col4}     |::|   |        {col5}      /::::::\    \        {reset}      
{col1}     /:::/\:::\    \     {col2}     /:::/\:::\    \     {col3}     /:::/\:::\    \     {col4}     |::|   |        {col5}     /:::/\:::\    \       {reset}      
{col1}    /:::/  \:::\    \    {col2}    /:::/  \:::\    \    {col3}    /:::/__\:::\    \    {col4}     |::|   |        {col5}    /:::/__\:::\    \      {reset}      
{col1}   /:::/    \:::\    \   {col2}   /:::/    \:::\    \   {col3}   /::::\   \:::\    \   {col4}     |::|   |        {col5}    \:::\   \:::\    \     {reset}      
{col1}  /:::/    / \:::\    \  {col2}  /:::/    / \:::\    \  {col3}  /::::::\   \:::\    \  {col4}     |::|___|______  {col5}  ___\:::\   \:::\    \    {reset}      
{col1} /:::/    /   \:::\ ___\ {col2} /:::/    /   \:::\ ___\ {col3} /:::/\:::\   \:::\____\ {col4}     /::::::::\    \ {col5} /\   \:::\   \:::\    \   {reset}      
{col1}/:::/____/  ___\:::|    |{col2}/:::/____/     \:::|    |{col3}/:::/  \:::\   \:::|    |{col4}    /::::::::::\____\{col5}/::\   \:::\   \:::\____\  {reset}      
{col1}\:::\    \ /\  /:::|____|{col2}\:::\    \     /:::|____|{col3}\::/    \:::\  /:::|____|{col4}   /:::/~~~~/~~      {col5}\:::\   \:::\   \::/    /  {reset}      
{col1} \:::\    /::\ \::/    / {col2} \:::\    \   /:::/    / {col3} \/_____/\:::\/:::/    / {col4}  /:::/    /         {col5} \:::\   \:::\   \/____/   {reset}      
{col1}  \:::\   \:::\ \/____/  {col2}  \:::\    \ /:::/    /  {col3}          \::::::/    /  {col4} /:::/    /          {col5}  \:::\   \:::\    \       {reset}      
{col1}   \:::\   \:::\____\    {col2}   \:::\    /:::/    /   {col3}           \::::/    /   {col4}/:::/    /           {col5}   \:::\   \:::\____\      {reset}      
{col1}    \:::\  /:::/    /    {col2}    \:::\  /:::/    /    {col3}            \::/____/    {col4}\::/    /            {col5}    \:::\  /:::/    /      {reset}      
{col1}     \:::\/:::/    /     {col2}     \:::\/:::/    /     {col3}             ~~          {col4} \/____/             {col5}     \:::\/:::/    /       {reset}      
{col1}      \::::::/    /      {col2}      \::::::/    /      {col3}                         {col4}                     {col5}      \::::::/    /        {reset}      
{col1}       \::::/    /       {col2}       \::::/    /       {col3}                         {col4}                     {col5}       \::::/    /         {reset}      
{col1}        \::/____/        {col2}        \::/____/        {col3}                         {col4}                     {col5}        \::/    /          {reset}      
{col1}                         {col2}         ~~              {col3}                         {col4}                     {col5}         \/____/           {reset}      
"""
