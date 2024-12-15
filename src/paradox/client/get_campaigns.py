import json
from asyncio import sleep, create_task
from itertools import chain, cycle

from app_state import state, on
from dateutil.parser import parse as dtparse
from django.db.models import Q, F
from django.core.serializers.json import DjangoJSONEncoder
from lockorator.asyncio import lock_or_exit
from loguru import logger

from . import base
from paradox.models import Campaign, Organization
from paradox import uix

        
mock_elections = [
    {
        'name': 'Выборы президента',
        'date': '2018.09.08',
        'coordinators': []
    }, 
    {
        'name': 'Выборы Депутатов МО Дачное',
        'date': '2018.09.08', 
        'munokrug': '6ab3-d1c23',
        'flags': ['otkrep', 'mestonah', 'dosrochka'],
        'region': 'ru_78',
        'coordinators': [{
            'org_id': '754',
            'org_name': 'Наблюдатели Петербурга',
            'contacts': [
                {
                    'type': 'tg', 
                    'name': 'НП общий чат', 
                    'value': 'https://t.me/spbelect_mobile',
                },
            ],
            'campaign': {
                'id': '8446',
                'contacts': [
                    {
                        'type': 'tg', 
                        'name': 'НП чат Кировский рн', 
                        'value': 'https://t.me/mobile_kir',
                    },
                    {
                        'type': 'ph', 
                        'name': 'НП Кировский', 
                        'value': '88121111'
                    }
                ],
            },
        }]
}]
        
@on('state.region')
@lock_or_exit()
@uix.homescreen.show_loader
@uix.organizations.show_loader
async def get_campaigns():
    await sleep(2)
    while True:
        region, country = state.get('region'), state.get('country')
        logger.info(f'Updating campaigns. Region: {getattr(region, "name", None)}, country: {country}')
        if not region.id or not country:
            logger.info('Skip updating campaigns until region and country is set.')
            return
        
        #data = (await base.recv_loop(f'{region.id}/elections/?include_coordinators=true')).json()
        data = (await base.recv_loop(f'{region.id}/elections/')).json()
        #data = mock_elections
        #logger.debug(data)
        
        for election in data:
            for coordinator in election['coordinators']:
                Organization.objects.update_or_create(id=coordinator['org_id'], defaults={
                    'name': coordinator['org_name'],
                    'contacts': json.dumps(coordinator['contacts'], ensure_ascii=False),
                })
                
                camp = coordinator['campaign']
                Campaign.objects.update_or_create(id=camp['id'], defaults={
                    'election_name': election.get('name'),
                    'country': country,
                    'region': election.get('region'), 
                    'munokrug': election.get('munokrug'), 
                    #'fromtime': dtparse(camp['fromtime']),
                    #'totime': dtparse(camp['totime']),
                    # TODO: fromisoformat, remove dateutil dep
                    'vote_date': dtparse(election['date']),
                    'coordinator_id': coordinator['org_id'],
                    'elect_flags': ','.join(election['flags']),
                    'contacts': json.dumps(camp['contacts'], ensure_ascii=False),
                })
        
        if (region, country) == (state.region, state.country):
            break  # Пока ожидали http ответ, регион не изменился, продолжим
        
        await sleep(5)
    
    create_task(update_elect_flags())
    campaigns = Campaign.objects.positional().current()
    logger.debug('Active election observers campaigns in current region: {}'.format(
        json.dumps(list(campaigns.values()), ensure_ascii=False, indent=2, cls=DjangoJSONEncoder)
    ))
    if campaigns.filter(munokrug__isnull=True).exists():
        state.superior_ik = 'TIK'
    else:
        state.superior_ik = 'IKMO'
    #uix.FormListScreen.delete_campaign_forms()
    #for campaign in campaigns:  #.filter(coordinator__subscription='yes'):
        #uix.formlist.show_campaign_forms(campaign)
    
    #if campaigns.count() == 0:
        #uix.formlist.show_no_campaign_notice()
        
    uix.organizations.show(Organization.objects.filter(campaigns__in=campaigns))
    #uix.coordinators.show(Organization.objects.all())
    logger.debug('Update campaigns finished')
    
    
@on('state.uik')
@lock_or_exit()
async def update_elect_flags():
    await sleep(0.5)
    campaigns = Campaign.objects.positional().current().filter(elect_flags__isnull=False)
    state.elect_flags = set(chain(*(x.elect_flags.split(',') for x in campaigns)))
    logger.debug(f'{campaigns.count()} active campaigns.')
    logger.debug(f'Election flags: {list(state.elect_flags)}')
    
        
