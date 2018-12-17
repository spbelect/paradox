{
    
    ('net/input_event/<iid>/send_start',
     'net/input_event/<iid>/send_success',
     'net/input_event/<iid>/send_error',
     'net/input_event/<iid>/send_fatal_error'): (
        'uix.base_input.Input',
        'models.InputEvent'),
     
    'uix/screens/userprofile/leave_changed': 'net.send_userprofile'
    
    'net/channel/<id>/message/sent':,
    'net/channel/<id>/message/received': 'models.Message.create',
    'net/channel/<id>/message/received': 'uix.screens.channels.add_unread',
    'net/channel/<id>/message/received': 'uix.side_panel.messages.add_unread',
    
    'uix/screens/channels/join/<id>': 'models.Channel.join'
    'uix/screens/channels/join/<id>': 'net.send_join_channel'
    'uix/screens/channels/leave/<id>': 'models.Channel.leave'
    'uix/screens/channels/leave/<id>': 'net.send_leave_channel'
}
     
{
    'state.inputs.<iid>': 'uix.base_input.Input'
    #'state.forms.general': 'uix.screens.form_screen.show_general'
    #'state.forms.campaign.<id>': 'uix.screens.form_screen.show_campaign'
}
    
{
    "inputs": [{
        "help_text": "ст. 68 п. 9,10\n9. При...",
        "input_type": "MULTI_BOOL",
        "elect_tags": {'otkrep': True},
        "dependants": {'24624': True},
        "depends_on": {'7634': False},
        "input_id": "8bc39338-67f0-4742-b9ec-d31206349fc5",
        "label": "ЧПСГ и наблюдатели видят все действия членов УИК",
        "alarm": {"eq": False}
      },]
}
    
{
    'mokruga': {'3467': {'name': 'МО Дачное', 'uiks': [[1, 498], 564]}, '47247': {}},
}

{
    'campaigns': {
        '8446': {
            'election': '6b26',
            'coordinator': '724',
            'fromtime': '2018.07.22T00:00',
            'totime': '2018.07.22T00:00',
            'channels': [
                {'type': 'readonly', 'uuid': '51', 'name': 'НП NEWS МО Дачное', 'icon': 'http://'},
                {'type': 'groupchat': 'uuid':'724', 'name': 'НП чат МО Дачное', 'icon': 'http://'},
            ],
            'external_channels': [{
                'type': 'tg', 'name': 'НП чат Кировский рн', 'link': 'https://t.me/mobile_kir',
            }],
            'phones': [{'name': 'НП Кировский', 'number': '88121111'}],
        },
    },
    'elections': {
        '6b26': {
            'name': 'Выборы Депутатов МО Дачное'
            'date': '2018.09.08', 
            'mokrug': '3467',
            'flags': ['otkrep', 'mestonah', 'dosrochka']
        },  
        'f674': {
            'name': 'Выборы президента'
        }},
    'coordinators': {'724':  {
        'name': 'Наблюдатели Петербурга',
        'external_channels': [{
            'type': 'tg', 
            'name': 'Общий чат СПб и ЛО', 
            'link': 'https://t.me/mobile_spb_lo',
            'region': '78',
        }],
        'phones': [{'name': 'НП Коллцентр', 'number': '88129535326'}],
        'channels': [
                {
                    'uuid': '7246',
                    'type': 'readonly',
                    'name': 'НП NEWS Спб',
                    'region': '78',
                    'icon': 'http://'}
                },
                {
                    'uuid': '886',
                    'type': 'groupchat',
                    'name': 'НП чат Спб',
                    'region': '78',
                    'icon': 'http://'}
                },
            ]
        }
    }
}
 
