import json

class LoadConfig(object):
    def __init__(self):
        f = open('config/config.json','r')
        config = json.loads(f.read())
        self.camera_num = config['camera_num']
        self.chat_id = config['chat_id']
        self.bot_token = config['bot_token']
        self.db_ip = config['db_ip']
        self.db_user = config['db_user']
        self.db_password = config['db_password']
        f.close()
        
    def saveConfig(self, camera_num, chat_id, bot_token,
                    db_ip, db_user, db_password):
        f = open('config/config.json','w+')
        config = json.dumps({
            'camera_num' : camera_num,
            'chat_id' : chat_id,
            'bot_token' : bot_token,
            'db_ip' : db_ip,
            'db_user' : db_user,
            'db_password' : db_password
        },indent=4, sort_keys=True)
        f.write(config)
        f.close()
    def defaultConfig(self):
        f = open('config/default_config.json','r')
        d = open('config/config.json','w+')
        d.write(f.read())
        f.close()
        d.close()
