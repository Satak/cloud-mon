import fastjsonschema

TOKEN_AUTH_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 30,
            "pattern": "^[A-Za-z0-9]*$"
        },
        'monitor_type': {
            'type': 'string'
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
        'monitor_type',
        'enabled',
        'base_url',
        'login_path',
        'monitor_path',
        'username',
        'password'
    ],
    'additionalProperties': False
}

BASIC_AUTH_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 30,
            "pattern": "^[A-Za-z0-9]*$"
        },
        'monitor_type': {
            'type': 'string'
        },
        'enabled': {
            'type': 'boolean'
        },
        'base_url': {
            'type': 'string',
            'minLength': 5,
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
        'monitor_type',
        'enabled',
        'base_url',
        'username',
        'password'
    ],
    'additionalProperties': False
}

NO_AUTH_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 30,
            "pattern": "^[A-Za-z0-9]*$"
        },
        'monitor_type': {
            'type': 'string'
        },
        'enabled': {
            'type': 'boolean'
        },
        'base_url': {
            'type': 'string',
            'minLength': 5,
            'maxLength': 100
        }
    },
    'required': [
        'name',
        'monitor_type',
        'enabled',
        'base_url'
    ],
    'additionalProperties': False
}

token_auth_validate = fastjsonschema.compile(TOKEN_AUTH_SCHEMA)
basic_auth_validate = fastjsonschema.compile(BASIC_AUTH_SCHEMA)
no_auth_validate = fastjsonschema.compile(NO_AUTH_SCHEMA)
