# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from asyncio import sleep

from app_state import state, on
from django.utils.timezone import now
from getinstance import InstanceManager
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from loguru import logger

from .vbox import VBox
from label import Label
from button import Button
from .choices import Choice
from paradox import utils
from .imagepicker import ImagePicker
from paradox.models import InputEventImage, InputEvent

Builder.load_string('''
#:include constants.kv

#:import state app_state.state

#:import uix paradox.uix

<Complaint>:
    #size_hint_y: None
    visible: False

    #padding: 0
    #spacing: 0
    #visible: True
    
    #json: self.input.json
    #example_uik_complaint: self.input.json['example_uik_complaint']
    
    Button:
        height: dp(20)
        size_hint_y: None
        #background_color: white
        #background_color: lightblue
        text: "Обжалование в УИК"
        color: black
        font_size: dp(20)
        #text: "Обжалование в УИК ◂"
        
        text_size: self.width, None
        #halign: 'left'
        
        Label:
            pos: self.parent.pos
            size: self.parent.size
            id: loader
            font_size: dp(20)
            opacity: 0
            text: 'загрузка...'
            background_color: wheat4
        
    BoxLayout:
        size_hint_y: None
        height: dp(22)
        padding: 0
        spacing: 0
        Button:
            #background_color: lightblue
            
            #halign: 'left'
            text_size: self.width, None
            height: dp(32)
            color: lightblue
            size_hint_y: None
            #background_color: white
            text: 'пример жалобы'
            font_size: dp(14)
            #he
            on_release: 
                uix.screenmgr.show_handbook(root.input.json['label'], root.uik_complaint_text)
            
        Button:
            #halign: 'right'
            text_size: self.width, None
            height: dp(32)
            size_hint_y: None
            color: lightblue
            text: 'правила обжалования'
            font_size: dp(14)
            on_release: uix.screenmgr.show_handbook('правила обжалования', 'TODO')

    Widget: #spacer
        height: dp(1)
        size_hint_y: None
        
    Label:
        font_size: dp(16)
        height: dp(16)
        size_hint_y: None
        text: 'сфотографируйте жалобу и акт'
        
        text_size: self.width, None
        #halign: 'left'
        
    ComplaintPhotoPicker:
        id: uik_complaint_images
        type: 'uik_complaint'
        input: root.input
        compress_quality: 40
        #on_image_picked: root.on_image_picked(filepath)
        
        
    Widget: #spacer
        height: dp(1)
        size_hint_y: None
        
    Label:
        font_size: dp(16)
        height: dp(16)
        size_hint_y: None
        
        text_size: self.width, None
        text: 'укажите статус жалобы'
        #halign: 'left'
        
    Choices:
        id: uik_complaint_status
        height: dp(18)
        font_size: dp(18)
        height: self.texture_size[1]
        modal_header: 'Статус жалобы'
        text: 'выберите статус'
        text_size: self.width, None
        #halign: 'left'
        on_text: self.color = black
        padding: 0, 0
        on_input: root.on_uik_complaint_status_input(self.value)
        size_hint_y: None
                
        ComplaintStatusChoice:
            value: 'none'
            text: 'не подавалась'
            short_text: 'не подавалась'
            
        ComplaintStatusChoice:
            value: 'refuse_to_accept'
            text: 'отказ принять жалобу'
            short_text: 'отказ принять жалобу'
            
        ComplaintStatusChoice:
            value: 'refuse_to_resolve'
            text: 'отказ рассмотрения жалобы'
            short_text: 'отказ рассмотрения'
            
        #ComplaintStatusChoice:
            #value: 'refuse_to_copy_reply'
            #text: 'отказ выдать копию решения'
            #short_text: 'отказ выдать копию решения'
            
        ComplaintStatusChoice:
            value: 'waiting_reply'
            text: 'ожидание решения комиссии'
            short_text: 'ожидание решения'
            
        ComplaintStatusChoice:
            value: 'got_unfair_reply'
            text: 'получено неудовлетворительное решение'
            short_text: 'получено неуд. решение'
            
        ComplaintStatusChoice:
            value: 'got_fair_reply'
            text: 'получено удовлетворительное решение'
            short_text: 'получено удовл. решение'

    Widget: #spacer
        height: dp(1)
        size_hint_y: None
        
    VBox:
        #id: uik_reply_images
        Label:
            font_size: dp(16)
            height: dp(16)
            size_hint_y: None
            text: 'сфотографируйте решение'
            
            text_size: self.width, None
            #halign: 'left'
            
        ComplaintPhotoPicker:
            id: uik_reply_images
            type: 'uik_reply'
            input: root.input
            compress_quality: 40
            #on_input: root.input.complaint_image_create(*args[1:])
            
    
    VBox:
        id: tik_complaint
        #size_hint: None, None
        size_hint_y: None
            
        #padding: 0
        #spacing: 0
        visible: False
            
        Widget: #spacer
            height: dp(1)
            size_hint_y: None
        
        Button:
            height: dp(20)
            size_hint_y: None
            text: "Обжалование в ТИК"
            color: black
            font_size: dp(20)
            #text: "Обжалование в ТИК ◂"
            
            text_size: self.width, None
            
            
        VBox:
            id: refuse_akt
            visible: False
            size_hint_y: None
            
            padding: 0
            spacing: 0
        
            Button:
                #halign: 'right'
                text_size: self.width, None
                height: dp(40)
                size_hint_y: None
                color: lightblue
                text: 'составьте акт об отказе'
                font_size: dp(14)
                on_release: uix.screenmgr.show_handbook('Составьте акт', root.refuse_akt_text())

            Widget: #spacer
                height: dp(1)
                size_hint_y: None
            
                
            Label:
                font_size: dp(16)
                height: dp(16)
                size_hint_y: None
                text: 'сфотографируйте акт'
                
                text_size: self.width, None
                #halign: 'left'
                
            ComplaintPhotoPicker:
                id: refuse_akt_images
                type: 'tik_complaint'
                input: root.input
                compress_quality: 40
                #on_image_picked: root.on_image_picked(filepath)
            
        
        
        VBox:
            id: refuse_person
            #visible: False
            size_hint_y: None
            
            #padding: 0
            spacing: 0
        
            Widget: #spacer
                height: dp(1)
                size_hint_y: None
                
            Label:
                font_size: dp(16)
                height: dp(16)
                size_hint_y: None
                
                text_size: self.width, None
                text: 'Укажите кому подавали жалобу'
                #halign: 'left'
                
            Choices:
                id: refuse_person_status
                height: dp(18)
                font_size: dp(18)
                height: self.texture_size[1]
                modal_header: 'Выберите статус'
                text: 'выберите статус'
                text_size: self.width, None
                #halign: 'left'
                on_text: self.color = black
                padding: 0, 0
                on_input: root.on_refuse_person(self.value)
                size_hint_y: None
                        
                RefusePersonChoice:
                    value: 'член комиссии'
                    text: 'член комиссии (или неизвестно)'
                    short_text: 'член комиссии'
                    
                RefusePersonChoice:
                    value: 'председатель'
                    text: 'председатель'
                    short_text: 'председатель'
                    
                RefusePersonChoice:
                    value: 'зам. председателя'
                    text: 'зам. председателя'
                    short_text: 'зам. председателя'
                    
                RefusePersonChoice:
                    value: 'секретарь'
                    text: 'секретарь'
                    short_text: 'секретарь'
                    
        Button:
            id: preview_tik_complaint
            height: dp(40)
            size_hint_y: None
            text: "Обжаловать по Email"
            color: teal
            font_size: dp(20)
            text_size: self.width, None
            on_release: 
                uix.screenmgr.show_handbook('Проверьте текст жалобы', root.tik_text)
            
            
#<ComplaintPhotoPicker>:

''')

class ComplaintStatusChoice(Choice):
    instances = InstanceManager()

class RefusePersonChoice(Choice):
    instances = InstanceManager()
    
    
class ComplaintPhotoPicker(ImagePicker):
    type = StringProperty()
    input = ObjectProperty()
    
    def on_image_picked(self, filepath):
        
        filepath = self.compress(filepath)
        #existing = InputEventImage.objects.filter()
        logger.info(f'create image {filepath}')
        dbimage, created = InputEventImage.objects.get_or_create(
            type=self.type, 
            event=self.input.last_event,
            filepath=filepath
        )
        
        logger.debug(list(InputEventImage.objects.values_list('filepath', flat=True)))
        if dbimage.deleted:
            logger.debug('undelete')
            dbimage.update(deleted=False, time_updated=now())
            uxitem = self.add_image(filepath)
            uxitem.dbid = dbimage.id
        elif created:
            uxitem = self.add_image(filepath)
            uxitem.dbid = dbimage.id
        
    def on_cross_click(self, cross):
        super().on_cross_click(cross)
        InputEventImage.objects.get(id=cross.parent.dbid).update(
            deleted=True,
            time_updated=now()
        )


whom = {
    None: 'члену комиссии',
    'член комиссии': 'члену комиссии',
    'председатель': 'председателю',
    'зам. председателя': 'заместителю председателя',
    'секретарь': 'секретарю'
}

whom2 = {
    None: 'члена комиссии',
    'член комиссии': 'члена комиссии',
    'председатель': 'председателя',
    'зам. председателя': 'заместителя председателя',
    'секретарь': 'секретаря'
}

uik_complaint_stub = '''
Жалоба

В Участковую Избирательную Комиссию {event.uik}, {region}
От кого: {profile.last_name} {profile.first_name} {profile.middle_name}, {role}.

Я, {profile.last_name} {profile.first_name}, находясь в помещении УИК {event.uik} {date} приблизительно в {event.time_created.hour} часов стал свидетелем нарушения [TODO: нарушения чего, по каждому инпуту]. Прошу рассмотреть жалобу на заседании комиссии и устранить нарушение. 

Прошу выдать мне заверенную копию решения комиссии.

Дата: {date} Время: ____

{profile.last_name} {profile.first_name} {profile.middle_name}, {role} <Подпись> тел.: +7 {profile.phone}
'''

tik_header = '''
Жалоба

В Территориальную Избирательную Комиссию {state.tik} {region}
От кого: {profile.last_name} {profile.first_name} {profile.middle_name}, {role}.
Дата: {date}

Я, {profile.last_name} {profile.first_name}, находясь в помещении УИК {event.uik} {date} приблизительно в {event.time_created.hour} часов стал свидетелем нарушения [TODO: нарушения чего, по каждому инпуту]. Составив жалобу, приложенную к данному письму, обратился к 
{whom} с просьбой принять жалобу и рассмотреть на заседании комиссии для устранения нарушения. 
'''

tik_footer = '''Прошу также рассмотреть мою жалобу по существу и донести решение до Участковой Избирательной Комииссии.

Прошу уведомить меня о принятии решения по телефону +7 {profile.phone}, а также выслать копию решения по электронной почте {profile.email}.

С уважением, {profile.last_name} {profile.first_name}.
'''

refuse_accept_stub = tik_header + """
Комиссия не стала рассматривать мою жалобу, в связи с чем был составлен акт, приложенный к данному письму.
Прошу признать бездействие Участковой Избирательной Комиссии незаконным. 
""" + tik_footer

refuse_resolve_stub = tik_header + """
{refuse_person_status} отказал мне в принятии жалобы, в связи с чем был составлен акт, приложенный к данному письму.
Прошу признать бездействие {whom2} незаконным.
""" + tik_footer

tik_complaint_stub = tik_header + """
Комиссия вынесла решение, противоречащее законодательству. Нарушение не устранено.
Прошу признать решение Участковой Избирательной Комииссии незаконным.
""" + tik_footer


akt_stub = '''
Попросите свидетелей поставить подписи и оставить телефон под актом. Телефон желательно оставить, так как в вышестоящей комиссии могут связаться со свидетелями для подтверждения\уточнения произошедшего.

Примерный текст:

Акт

Мы, нижеподписашиеся, находясь в помещении УИК {event.uik} {date}, приблизительно в {event.time_created.hour} часов стали свидетелями того, как {role} {profile.first_name} {profile.last_name} обратился к (секретарю\председателю\...) с просьбой (принять\рассмотреть) жалобу на возможное нарушение.
(Комиссия\председатель\...) (не стала рассматривать\отказалась принять жалобу\отказалась выдать копию решения\...)

Дата: {date} Время: ____

{profile.last_name} {profile.first_name} {profile.middle_name}, {role} <Подпись> тел.: +7 {profile.phone}
<ФИО>, <Статус> <Подпись> <Телефон>
<ФИО>, <Статус> <Подпись> <Телефон>
...
'''

roles = {
    'prg': 'член комиссии с правом решающего голоса',
    'psg': 'член комиссии с правом совещательного голоса',
    'nabludatel': 'наблюдатель',
    'smi': 'журналист',
    'kandidat': 'кандидат',
    'izbiratel': 'избиратель',
    'other': 'избиратель',
}

class Complaint(VBox):
    input = ObjectProperty()
    tik_text = StringProperty(None, allow_none=True)
    uik_complaint_text = StringProperty(None, allow_none=True)
    
    def refuse_akt_text(self):
        return akt_stub.format(**self.context())
    #event = ObjectProperty(None, allow_none=True)
    
    
    #def do_layout(self, *args):
        ##import ipdb; ipdb.sset_trace()
        #return super().do_layout(*args)
        
    async def on_event(self, event):
        #logger.debug(event, event.revoked)
        if event is None:
            self.visible = False
            return
        
        if event.revoked or not event.alarm:
            self.visible = False
            return
            
        #print('conmpl1')
        self.visible = True
        self.ids.loader.opacity = 1
        self.ids.uik_complaint_status.choice = ComplaintStatusChoice.instances.get(
            value=event.uik_complaint_status
        )
        #print('conmpl2')
        if event.uik_complaint_status in ['got_unfair_reply', 'refuse_to_accept', 'refuse_to_resolve']:
            self.ids.tik_complaint.visible = True
            
            if event.uik_complaint_status == 'refuse_to_accept':
                self.ids.refuse_person.visible = True
                
        #print('conmpl3')
        self.ids.refuse_person_status.choice = RefusePersonChoice.instances.get(
            value=event.refuse_person
        )
        self.toggle_tik(event.uik_complaint_status)
        self.build_uik_text()
        
        #print('conmpl4')
        await sleep(0.01)
        
        #print('conmpl5')
        self.ids.uik_complaint_images.del_images()
        self.ids.uik_reply_images.del_images()
        
        logger.debug(f'{self.input.json["label"]}: {event.images.count()} images for event {event.id}')
        for dbimage in event.images.all():
            if dbimage.deleted:
                logger.debug(f'image {dbimage.filepath} was deleted by user')
                continue
            
            if dbimage.type == 'uik_complaint':
                uxitem = self.ids.uik_complaint_images.add_image(dbimage.filepath)
            elif dbimage.type == 'uik_reply':
                uxitem = self.ids.uik_reply_images.add_image(dbimage.filepath)
            elif dbimage.type == 'tik_complaint':
                uxitem = self.ids.refuse_akt_images.add_image(dbimage.filepath)
                
            uxitem.dbid = dbimage.id
            await sleep(0.01)
                #('tik_complaint', 'Подаваемые в ТИК жалобы'),
                #('tik_reply', 'Ответы, решения от ТИК'),'
        self.ids.loader.opacity = 0
                
    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        
    def on_uik_complaint_status_input(self, value):
        logger.debug(f'{self.input.last_event.id}, {value}')
        InputEvent.objects.filter(id=self.input.last_event.id).update(
            uik_complaint_status=value, time_updated=now()
        )
        self.toggle_tik(value)
        
        
    def toggle_tik(self, uik_complaint_status):
        refuse = ['refuse_to_accept', 'refuse_to_resolve', 'refuse_to_copy_reply']
        if uik_complaint_status in ['got_unfair_reply'] + refuse:
            self.ids.tik_complaint.visible = True
            
            if uik_complaint_status in refuse:
                self.ids.refuse_akt.visible = True
            else:
                self.ids.refuse_akt.visible = False
                
        else:
            self.ids.tik_complaint.visible = False
        self.build_tik_text()
        
    def on_refuse_person(self, value):
        InputEvent.objects.filter(id=self.input.last_event.id).update(
            refuse_person=value
        )
        self.build_tik_text()
        
    def context(self):
        #event = self.input.last_event
        return dict(
            event=self.input.last_event,
            date=self.input.last_event.time_created.strftime('%d.%m.%Y'),
            profile=state.profile,
            refuse_person_status=self.ids.refuse_person_status.value or 'член комиссии',
            state=state, 
            whom2 = whom2[self.ids.refuse_person_status.value], 
            whom=whom[self.ids.refuse_person_status.value],
            role=roles[self.input.last_event.role],
            region=state.regions.get(self.input.last_event.region).name
        )
    
    @on('state.profile')
    def build_tik_text(self):
        #args = 
        if self.ids.uik_complaint_status.value == 'refuse_to_accept':
            self.tik_text = refuse_accept_stub.format(**self.context())
        elif self.ids.uik_complaint_status.value == 'refuse_to_resolve':
            self.tik_text = refuse_resolve_stub.format(**self.context())
        else:
            # 'got_unfair_reply'
            self.tik_text = tik_complaint_stub.format(**self.context())

    @on('state.profile')
    def build_uik_text(self):
        #input.json['example_uik_complaint']
        self.uik_complaint_text = uik_complaint_stub.format(**self.context())
        
            
        
