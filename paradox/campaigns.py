
async def on_subscribe(id):
    Campaign.objects.filter(id=id).update(subscription='subing')
    subscribe(id)
    
    
@screens.formlist.show_campaign_forms_loader
@lock_wait('campaign_sub')   
async def subscribe(id):
    while True:
        try:
            response = await asks.post(f'{state.server}/campaigns/{id}/subscribe/')
        except Exception as e:
            uix.screens.campaigns.subscribe_error(id)
        else:
            if response.status_code == 200:
                break
            uix.screens.campaigns.subscribe_error(id)
        trio.sleep(5)
    
    campaign = Campaign.objects.get(id=id)
    if not campaign.subscription == 'subing':
        return  # Пока ожидали http ответ, юзер отписался
    
    filter = Q(campaign=campaign) | Q(coordinator=campaign.coordinator)
    Channel.objects.filter(filter, actual=True).update(joined=True)
                
    formdata = await recv_loop(f'/campaigns/{id}/forms/')
    
    for form in formdata:
        for input in form['inputs']:
            state.inputs[input['id']] = input
                
    if not state.forms.campaign[id] == formdata:
        state.forms.campaign[id] = formdata
        campaign = Campaign.objects.get(id=id)
        if campaign.region == None \
           or (campaign.region == state.region.id and campaign.mokrug == None) \
           or campaign.mokrug == state.mokrug:
            uix.screens.formlist.show_campaign_forms(id)
    
    Campaign.objects.filter(id=id).update(subscription='yes')
    uix.screens.campaigns.subscribe_success(id)
    
            
async def on_unsubscribe(id):
    Campaign.objects.filter(id=id).update(subscription='unsubing')
    unsubscribe(id)
    
    
@uix.screens.formlist.show_campaign_forms_loader
@lock_wait('campaign_sub')
async def unsubscribe(id):
    while True:
        try:
            response = await asks.post(f'{state.server}/campaigns/{id}/unsubscribe/')
        except Exception as e:
            uix.screens.campaigns.unsubscribe_error(id)
        else:
            if response.status_code == 200:
                break
            uix.screens.campaigns.unsubscribe_error(id)
        trio.sleep(5)
    
    if not Campaign.objects.get(id=id).subscription == 'unsubing':
        return  # Пока ожидали http ответ, юзер подписался
    
    uix.screens.formlist.remove_campaign_forms(id)
    Campaign.objects.filter(id=id).update(subscription='no')
    
    
@uix.screens.formlist.show_campaign_forms_loader
@uix.screens.campaigns.show_loader
@lock_or_exit('update_campaigns')
async def update_campaigns():
    while True:
        region = state.region
        data = await recv_loop(f'/country/{state.country}/region/{region}/campaigns/')
        
        Channel.objects.filter(coordinator__in=data['coordinators']).update(actual=False)
                
        for id, coordinator in data['coordinators'].items():
            Coordinator.objects.update_or_create(id=id, {
                'name': coordinator['name'],
                
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
                'coordinator'
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
    uix.screens.campaigns.show(campaigns)
    
    uix.screens.formlist.delete_campaign_forms()
    for campaign in campaigns.filter(subscription='yes'):
        uix.screens.formlist.show_campaign_forms(state.forms.campaign[campaign.id])
        
