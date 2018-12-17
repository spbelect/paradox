

@lock_or_exit('send_position')
async def send_position():
    while True:
        uik, region = state.uik, state.region
        try:
            response = await asks.post(f'{state.server}/position/', {
                'app_id': state.app_id,
                'uik': state.uik,
                'region': state.region,
                'country': state.country,
            })
        except Exception as e:
            pass
        else:
            if response.status_code == 200:
                if not (uik, region) == (state.uik, state.region):
                    # Пока ожидали http ответ, уик\регион изменился, пошлем новые
                    continue  
                break
            else:
                uix.sidepanel.http_error(response)
        trio.sleep(5)
    

#@lock_wait('start')
async def on_start():
    Campaign.objects.exclude(fromtime__gt=now(), totime__lt=now()).update(active=False)
    Campaign.objects.filter(fromtime__gt=now(), totime__lt=now()).update(active=True)
    
    for campaign in Campaign.objects.filter(subscription='subing'):
        campaigns.subscribe(campaign.id)
        
    for campaign in Campaign.objects.filter(subscription='unsubing'):
        campaigns.unsubscribe(campaign.id)
    
    formdata = await recv_loop(f'/forms/general/')
    
    for form in formdata:
        for input in form['inputs']:
            state.inputs[input['id']] = input
            
    if not state.forms.general == formdata:
        state.forms.general = formdata
        screens.formlist.build_general_forms(formdata[state.country])
    
    state.regions = await recv_loop('/regions/')
    state.region = state.regions[state.region_id]
    mo = get_mokrug(state.region, state.uik)
    
    await campaigns.update_campaigns()
