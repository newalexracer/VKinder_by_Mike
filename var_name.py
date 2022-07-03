import os

database_name = os.getenv('DATABASE_NAME_VKINDER',
                          default='postgresql://user_vkinder:pass_vkinder@localhost:5432/vkinder')
token_group = os.getenv('TOKEN_GROUP_VKINDER', default=None)
token_app = os.getenv('TOKEN_APP_VKINDER', default=None)