from libtera.redis.RedisRPCClient import RedisRPCClient
from libtera.ConfigManager import ConfigManager
from modules.BaseModule import ModuleNames, create_module_message_topic_from_name

from datetime import datetime

if __name__ == '__main__':
    config = ConfigManager()
    config.load_config('../../config/TeraServerConfig.ini')

    start_time = datetime.now()

    rpc = RedisRPCClient(config.redis_config)
    for i in range(0, 1000):
        status_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'status_users')

    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    print('Time : ', elapsed, 'Rate Hz',  1000.0 / float(elapsed))



