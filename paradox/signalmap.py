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

