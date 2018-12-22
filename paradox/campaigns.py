
async def on_subscribe(id):
    Coordinator.objects.filter(id=id).update(subscription='subing')
    subscribe(id)
    
    
@uix.formlist.show_loader
@lock_wait('coordinator_sub')   
async def subscribe(id):
    while True:
        try:
            response = await asks.post(f'{state.server}/coordinators/{id}/subscribe/')
        except Exception as e:
            uix.coordinators.subscribe_error(id)
        else:
            if response.status_code == 200:
                break
            uix.coordinators.subscribe_error(id)
        trio.sleep(5)
    
    coordinator = Coordinator.objects.get(id=id)
    if not coordinator.subscription == 'subing':
        return  # Пока ожидали http ответ, юзер отписался
    
    #campaigns = 
    #filter = Q(campaign__in=campaigns) | Q(campaign__isnull=True)
    #Channel.objects.filter(filter, coordinator=id, actual=True)
    coordinator.channels.filter(campaign__isnull=True, actual=True).update(joined=True)
    
    for campaign in Campaign.objects.positional().filter(coordinator=id):
        campaign.channels.filter(actual=True).update(joined=True)
        
        formdata = await recv_loop(f'/campaigns/{campaign.id}/forms/')
        
        for form in formdata:
            for input in form['inputs']:
                state.inputs[input['id']] = input
                    
        if not state.forms.campaign[campaign.id] == formdata:
            state.forms.campaign[campaign.id] = formdata
            uix.formlist.show_campaign_forms(campaign)
        
    Coordinator.objects.filter(id=id).update(subscription='yes')
    uix.messages.show_channels(Channel.objects.filter(joined=True))
    uix.coordinators.subscribe_success(id)
    
            
async def on_unsubscribe(id):
    Coordinator.objects.filter(id=id).update(subscription='unsubing')
    unsubscribe(id)
    
    
@uix.formlist.show_loader
@lock_wait('coordinator_sub')
async def unsubscribe(id):
    while True:
        try:
            response = await asks.post(f'{state.server}/coordinators/{id}/unsubscribe/')
        except Exception as e:
            uix.coordinators.unsubscribe_error(id)
        else:
            if response.status_code == 200:
                break
            uix.coordinators.unsubscribe_error(id)
        trio.sleep(5)
    
    if not Coordinator.objects.get(id=id).subscription == 'unsubing':
        return  # Пока ожидали http ответ, юзер подписался
    
    for campaign in Campaign.objects.filter(coordinator=id):
        uix.formlist.remove_campaign_forms(campaign.id)
    Coordinator.objects.filter(id=id).update(subscription='no')
    
    
@uix.formlist.show_campaign_forms_loader
@uix.coordinators.show_loader
@lock_or_exit('update_campaigns')
async def update_campaigns():
    while True:
        region = state.region
        data = await recv_loop(f'/region/{region}/campaigns/')
        
        Channel.objects.filter(coordinator__in=data['coordinators']).update(actual=False)
                
        for id, coordinator in data['coordinators'].items():
            Coordinator.objects.update_or_create(id=id, {
                'name': coordinator['name'],
                'phones': json.dumps(coordinator['phones'])
            })
            for channel in coordinator['channels']:
                Channel.objects.update_or_create(id=channel['id'], {
                    'name': channel['name'],
                    'actual': True,
                    'coordinator': id,
                })
        
        for id, campaign in data['campaigns'].items():
            election = data['elections'].get(campaign['election'])
            Campaign.objects.update_or_create(id=id, {
                'region': election.get('region'), 
                'mokrug': election.get('mokrug'), 
                'fromtime': campaign['fromtime'],
                'totime': campaign['totime'],
                'coordinator': campaign['coordinator'],
                'elect_flags': ','.join(election['flags']),
            })
            for channel in campaign['channels']:
                Channel.objects.update_or_create(id=channel['id'], {
                    'name': channel['name'],
                    'actual': True,
                    'campaign': id,
                    'coordinator': campaign['coordinator']
                })
        
        if region == state.region:
            break  # Пока ожидали http ответ, регион не изменился, продолжим
        
        trio.sleep(5)
    
    campaigns = Campaign.objects.positional().filter(active=True)
    uix.coordinators.show(Coordinator.objects.filter(campaign__in=campaigns))
    
    uix.formlist.delete_campaign_forms()
    for campaign in campaigns.filter(coordinator__subscription='yes'):
        uix.formlist.show_campaign_forms(campaign)
    
    if campaigns.filter(coordinator__subscription='yes').count() == 0:
        uix.formlist.show_no_coordinator_notice()
