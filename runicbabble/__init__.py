import runicbabble.config

# top-level defaults
runicbabble.config.from_dict({
    'db': {
        'main': {
            'location': 'sqlite:///runic.sqlite'
        }
    }
})

# read user config directory
runicbabble.config.from_directory('config')

# read environment variables
runicbabble.config.from_env_mapping({
    'discord': {
        'bot_token': 'BOT_TOKEN'
    },
    'db': {
        'main': {
            'location': 'DB_LOCATION'
        }
    }
})
