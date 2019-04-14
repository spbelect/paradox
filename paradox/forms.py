
def on_input(iid, value):
    if App.screens.get_screen('position').userprofile_errors():
        App.screens.push_screen('userprofile')
        return

    if App.screens.get_screen('position').show_errors():
        App.screens.push_screen('position')
        return

    timestamp = datetime.utcnow()
    position = App.app_store.get('position', {})

    event = {
        'timestamp': timestamp.isoformat(),
        'uik': position.get('uik'),
        'region_id': position.get('region_id'),
        'input_id': input.input_id,
        'value': value}

    event = InputEvent.objects.create(
        input_id=iid,
        input_label=state.inputs[iid].label,
        country=state.country,
        region=state.region,
        uik=state.uik,
    )
    
    #campaigns = Campaign.objects.positional().filter(active=True, subscription='yes')
    #event.coordinators = [x.coordinator.id for x in campaigns]

    #eid = App.event_store.insert(dict(event, title=event_title))

    for input in uix.Input.instances.find(iid=iid):
        input.on_save_success(eid, timestamp, value)
    uix.screens.events.add_event(dict(event, title=event_title))


async def send_loop():
    while True:
        tosend = Q(send_status__in=['pending', 'exception']) | Q(send_status__startswith='http_')
        #pending = InputEvent.objects.filter(tosend)
        for event in InputEvent.objects.filter(tosend).values():
            try:
                response = await asks.post('{state.server}/input_events/', {
                    'iid': event.input_id,
                    #'coordinators': [x.id]
                })
            except Exception as e:
                event.update(send_status='exception')
                uix.Input.instances.find(iid=iid).on_send_error(event)
                break
            if not response.status_code == 200:
                event.update(send_status=f'http_{response.status_code}')
                uix.Input.instances.find(iid=iid).on_send_error(event)
                break
            event.update(send_status='sent')
            uix.Input.instances.find(iid=iid).on_send_success(event)
        trio.sleep(5)
        
        
async def recv_loop(url):
    while True:
        try:
            response = await asks.get('{state.server}{url}')
        except Exception as e:
            trio.sleep(5)
        else:
            return response
            
        

            
