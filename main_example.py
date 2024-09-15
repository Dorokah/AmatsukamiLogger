import os
from AmatsukamiLogger import logger, initialize
import warnings

initialize(False, log_level="DEBUG", service_name="logger_example")

warnings.warn("Warning test")

logger.debug("I`m debug")

with logger.contextualize(path="Music", request_id="07f33010-77a5-11ec-ac21-ae1d19e4fa20"):
    logger.info("I`m info with str extra field", contact_id="Noa Kirel")
    logger.warning("I`m warn with extra dict:", some_dict={"numbers": [4, 8, 3]})

logger.error("I`m error")
logger.critical("I`m critical")
logger.warning("This is a log with list and simple type:", is_exmaple=True, some_list=["a", "b", "c"])

try:
    raise Exception("Some Exception")
except Exception as exc:
    logger.exception(exc)

os.environ['COMMIT_HASH'] = 'some_hash'
initialize(log_to_stdout=True,
           log_file_name="my_logs.log",
           enable_json_logging=True,
           enable_datadog_support=False,
           service_name="logger_example",
           local_logs_extra_types={'rotation': "1 MB"})

try:
    raise Exception("Some Exception")
except Exception as exc:
    logger.exception(exc)

try:
    raise Exception("this is Exception with dicts")
except Exception as exc2:
    logger.exception(str(exc2),
                     request_id="another_request",
                     pokemon_id="Pikachu",
                     person_id="23132161891161515616116516515615157615785",  # this is longer then 40 chars
                     dict1={"numbers": [4, 8, 3]},
                     dict2={"strings": "Hello"})

initialize(False, log_level="DEBUG", service_name="logger_example")
@logger.catch
def logger_catch_decorator_example(x, y, z):
    # An error? It's caught anyway!
    return 1 / (x + y + z)


logger_catch_decorator_example(0, 0, 0)
