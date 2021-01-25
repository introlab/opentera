from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.config.ConfigManager import ConfigManager
from opentera.modules.BaseModule import ModuleNames

from datetime import datetime

if __name__ == '__main__':
    config = ConfigManager()
    config.load_config('../../config/TeraServerConfig.ini')

    start_time = datetime.now()
    rpc = RedisRPCClient(config.redis_config)

    count = 10000
    for i in range(count):
        status_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'status_users')

    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    print('Time : ', elapsed, 'Rate Hz', float(count) / float(elapsed))



