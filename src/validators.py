import fastjsonschema

MONITOR_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 30,
            "pattern": "^[A-Za-z0-9]*$"
        },
        'enabled': {
            'type': 'boolean'
        },
        'base_url': {
            'type': 'string',
            'minLength': 5,
            'maxLength': 100
        },
        'login_path': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 100
        },
        'monitor_path': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 100
        },
        'username': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 30
        },
        'password': {
            'type': 'string',
            'minLength': 0,
            'maxLength': 100
        }
    },
    'required': [
        'name',
        'enabled',
        'base_url',
        'login_path',
        'monitor_path',
        'username',
        'password'
    ],
    'additionalProperties': False
}

validate_monitor = fastjsonschema.compile(MONITOR_SCHEMA)
