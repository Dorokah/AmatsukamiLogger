# AmatsukamiLogger
<img src="./example.gif" alt="">

### Experience advanced log handling with divine precision.
Named after Kotoamatsukami, this package offers unparalleled control and organization, akin to how Kotoamatsukami subtly manipulates perception. <br/>
Did you ever feel confused about how logs are being configured looks and work with `DATADOG`<br/>
How many times' did you use `print()` in a simple code instead?...<br/>
logging is fundamental to every application and eases the process of debugging.<br/>
Using logger you have no excuse not to use logging from the start, For Much more pleasant and powerful logging
experience.<br/>

## 🚀 Features

- Support pretty local log format with predefined schema and colors.
- Support both `JSON` logs (for `DATADOG`) and `PLAIN TEXT` logs by config.
- Support `DATADOG` tags.
- Support dynamic const fields like `request_id`.
- Support multiple `Dict`s pretty print.
- Fast `Json` dumping using `orjson`.
- You can use any of [loguru](https://github.com/Delgan/loguru) features with this package.
- Support For `Python 3.11` and above.
- Support redirecting 3rd party packages loggers.
- Support for redirecting warnings messages displayed by `warnings.warn`

## Usage and Examples:

### Basic usage:

```
from AmatsukamiLogger import logger, initialize

initialize(enable_json_logging=False, log_level="DEBUG", service_name="some_service")

logger.debug("I`m debug")

with logger.contextualize(path="Music", request_id="07f33010-77a5-11ec-ac21-ae1d19e4fa20"):
    logger.info("I`m info with str extra field", contact_id="Noa Kirel")
    logger.warning("I`m warn with extra dict:", some_dict={"numbers": [4, 8, 3]})
```

#### Will print:

Unfortunately colors can't be seen in this markdown file.

```
|DEBUG| 2022-02-07 15:32:53:703 |68bfcee| dor.rokah-MacbookPro | ll_exmaple | main_example:7
I`m debug
|INFO| 2022-02-07 15:32:53:704 |68bfcee| dor.rokah-MacbookPro | ll_exmaple | main_example:10 | request_id:07f33010-77a5-11ec-ac21-ae1d19e4fa20 | contact_id:Noa Kirel | path:Music
I`m info with str extra field
|WARNING| 2022-02-07 15:32:53:704 |68bfcee| dor.rokah-MacbookPro | ll_exmaple | main_example:11 | request_id:07f33010-77a5-11ec-ac21-ae1d19e4fa20 | path:Music
I`m warn with extra dict:
{
  "some_dict": {
    "numbers": [
      4,
      8,
      3
    ]
  }
}
```

Any logs nested under:`logger.contextualize(path="Music", request_id="pouch")`<br/>
Will have the extra fields: `path="Music", request_id="pouch"`<br/>

Notice you can add any extra values that you want to the log.<br/>
If it is possible to inline the value in the first log line it will.<br/>
if not it will pretty print any enter type value in a new row after the message line.<br/>
You can view more examples below. <br/>

#### When `enable_json_logging=True`:
```
{"timestamp":"2022-02-07 15:35:19.587305+02:00","message":"I`m debug","commit":"68bfcee","service_name":"ll_exmaple","hostname":"dor.rokah-MacbookPro","level":"DEBUG","dd.trace_id":"0","dd.span_id":"0","dd.env":"","dd.service":"","dd.version":""}
{"timestamp":"2022-02-07 15:35:19.587890+02:00","message":"I`m info with str extra field","commit":"68bfcee","service_name":"ll_exmaple","hostname":"dor.rokah-MacbookPro","level":"INFO","dd.trace_id":"0","dd.span_id":"0","dd.env":"","dd.service":"","dd.version":"","path":"Music","request_id":"07f33010-77a5-11ec-ac21-ae1d19e4fa20","contact_id":"Noa Kirel"}
{"timestamp":"2022-02-07 15:35:19.588085+02:00","message":"I`m warn with extra dict:","commit":"68bfcee","service_name":"ll_exmaple","hostname":"dor.rokah-MacbookPro","level":"WARNING","dd.trace_id":"0","dd.span_id":"0","dd.env":"","dd.service":"","dd.version":"","path":"Music","request_id":"07f33010-77a5-11ec-ac21-ae1d19e4fa20","some_dict":{"numbers":[4,8,3]}}
```

## The Log schema:

```
|LEVEL| YYYY-MM-DD HH:mm:ss:SSS |GIT_HASH| HOSTNAME | SERVICE_NAME | MODULE:LINE | INLINE_EXTRAS 
MESSAGE
EXTRAS
```

#### logger.exception(exception:Exception):

```
|LEVEL| YYYY-MM-DD HH:mm:ss:SSS |GIT_HASH| HOSTNAME | SERVICE_NAME | MODULE:LINE | INLINE_EXTRAS | EXCEPTION_TYPE
EXCEPTION_MESSAGE
STACKTRACE
EXTRAS
```

## Configuration:

`initialize` - Creates A logger config log handler and set loguru to use that handler.

```
Creates A logger config log handler and set loguru to use that handler.
Parameters
----------
enable_json_logging : bool
  when enabled logs will be sent in json format.
enable_datadog_support : bool
  when enabled Datadog tags will be added, used for correlation between logs and metrics.
service_name : str,
  field which will be in every log (default is "unnamed_service")
log_level : str,
  TRACE < DEBUG < INFO < SUCCESS < WARNING < ERROR, EXCEPTION < CRITICAL (default is INFO)
local_logs_extra_types : [type],
  list of logs fields types which will be added to the first line in the log if possible
  (default is [int, float, bool]) plus str which does not have \n in them and their length do not pass 40 chars
log_to_stdout : bool,
  flag used to enable logging to stdout (default is True)
log_file_name : str,
  flag used to enable logging to a file the value will be the file logs file name (default is None)
loguru_stdout_extras : dict,
  dict for extra args that can be pass down the logger.add() method in loguru only stdout combinable fields will work.
  https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
loguru_log_file_extras : dict,
  dict for extra args that can be pass down the logger.add() method in loguru only file log combinable fields will work.
  https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
redirect_3rd_party_loggers : bool,
  flag used to redirect all loggers handlers that being used to loguru logger (default is False)
redirect_warnings : bool,
  flag used to redirect all warnings.warn() to logger.warning() (default is True)
suppress_standard_logging : dict{logger_name[str]: log_level[int]},
  list of loggers by their names which will be set to the desired log level (default is None)
enable_colors : bool,
  flag used to enable to display colored logs by their level, this options only relevant
  when logging to the console (default is True)
    
```

# More Examples:

### Errors and custom types printing:

```
initialize(log_to_stdout=True,
           log_file_name="my_logs.log",
           enable_json_logging=False,
           service_name="ll_exmaple",
           enable_stackprinter_stacktrace=True,
           local_logs_extra_types={'rotation': "1 MB"})

logger.error("I`m error")
logger.critical("I`m critical")
logger.warning("This is a log with list and simple type:", is_exmaple=True, some_list=["a", "b", "c"])
```

#### Will print (will also be written to a file called "my_logs.log"):

```
|ERROR| 2022-02-07 15:41:41:296 |68bfcee| dor.rokah-MacbookPro | ll_exmaple | main_example:21
I`m error
|CRITICAL| 2022-02-07 15:41:41:297 |68bfcee| dor.rokah-MacbookPro | ll_exmaple | main_example:22
I`m critical
|WARNING| 2022-02-07 15:41:41:297 |68bfcee| dor.rokah-MacbookPro | ll_exmaple | main_example:23
This is a log with list and simple type:
{
  "is_exmaple": true,
  "some_list": [
    "a",
    "b",
    "c"
  ]
}

```

#### Exception:

```
try:
    raise Exception("Some Exception")
except Exception as exc:
    logger.exception(exc)
```

#### Will print:

```
|EXCEPTION| 2024-09-16 00:46:09:013 |043b38c| Dor_YOGA_Pro | logger_example | main_example:22
|Exception| Some Exception: | Some Exception
Traceback (most recent call last):
  File "C:\Users\dorro\code\AmatsukamiLogger\main_example.py", line 20, in <module>
    raise Exception("Some Exception")
Exception: Some Exception
```

#### @logger.catch :

```
@logger.catch
def logger_catch_decorator_example(x, y, z):
    # An error? It's caught anyway!
    return 1 / (x + y + z)


logger_catch_decorator_example(0, 0, 0)

```

#### Will print:

```
|EXCEPTION| 2024-09-16 00:47:59:366 |some_hash| Dor_YOGA_Pro | logger_example | main_example:54
|ZeroDivisionError| division by zero: | An error has been caught in function '<module>', process 'MainProcess' (38684), thread 'MainThread' (23348):
Traceback (most recent call last):
  File "C:\Users\dorro\code\AmatsukamiLogger\.venv\Lib\site-packages\loguru\_logger.py", line 1277, in catch_wrapper
    return function(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\dorro\code\AmatsukamiLogger\main_example.py", line 51, in logger_catch_decorator_example
    return 1 / (x + y + z)
           ~~^~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

### Notes:
 * logs in `DataDog` at level `SUCCESS` will shop up as `INFO` in `DataDog`.
 * logs in `DataDog` at level `TRACE` will not show up in `DataDog`.