class XorKeys:
    """XOR keys for GD specific responses."""

    PASSWORD = 37526
    CHK = 19847
    LEVEL_PASSWORD = 26364
    QUESTS = 19847
    CHESTS = 59182


class Permissions:
    """GDPyS action permissions."""

    AUTH = 2 << 0
    UPLOAD_LEVEL = 2 << 1
    POST_COMMENT = 2 << 2
    POST_ACC_COMMENT = 2 << 3
    MOD_REGULAR = 2 << 6
    MOD_ELDER = 2 << 7
    MOD_RATE = 2 << 8


class Secrets:
    """All the GeometryDash secret values"""

    NORMAL = "Wmfd2893gb7"


class ResponseCodes:
    """All the web response codes."""

    GENERIC_FAIL = "-1"
    GENERIC_SUCCESS = "1"
    GENERIC_FAIL2 = "-2"
    GENERIC_SUCCESS2 = "2"
    LOGIN_CONTACT_ROB = "-12"
    EMPTY_LIST = "#0:0:0"
    COMMENT_BAN = "-10"


class Colours:
    """ALL THE COLOURS IN THE SKY"""

    RESET = u"\u001b[0m"
    RED = u"\u001b[31m"
    BLACK = u"\u001b[30m"
    GREEN = u"\u001b[32m"
    YELLOW = u"\u001b[33m"
    BLUE = u"\u001b[34m"
    MAGENTA = u"\u001b[35m"
    CYAN = u"\u001b[36m"
    WHITE = u"\u001b[37m"
    ALL_COL = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]


class CryptKeys:
    SOLO = "xI25fpAapCQg"
    SOLO3 = "oC36fpYaPtdg"
    SOLO4 = "pC26fpYaQCtg"


class Paths:
    """File paths."""

    LANG_PACKS = "lang/"


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
