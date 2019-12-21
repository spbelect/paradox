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
from paradox.models import AnswerImage, Answer

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
    
    #width: 0.9 * getattr(self.parent, 'width', 10)
    #json: self.quizwidget.json
    #example_uik_complaint: self.quizwidget.json['example_uik_complaint']
    
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
                uix.screenmgr.show_handbook(root.quizwidget.json['label'], root.uik_complaint_text)
            
        Button:
            #halign: 'right'
            text_size: self.width, None
            height: dp(32)
            size_hint_y: None
            color: lightblue
            text: 'правила обжалования'
            font_size: dp(14)
            on_release: uix.screenmgr.show_handbook('правила обжалования', root.complaint_rules)

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
        quizwidget: root.quizwidget
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
        
    ChoicePicker:
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
        on_new_pick: root.on_uik_complaint_status_input(self.value)
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
            quizwidget: root.quizwidget
            compress_quality: 40
            #on_new_pick: root.quizwidget.complaint_image_create(*args[1:])
            
    
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
                quizwidget: root.quizwidget
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
                
            ChoicePicker:
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
                on_new_pick: root.on_refuse_person(self.value)
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
                uix.screenmgr.show_tik_complaint(root)
                #uix.screenmgr.show_handbook('Проверьте текст жалобы', root.tik_text)
            
            
#<ComplaintPhotoPicker>:

''')

class ComplaintStatusChoice(Choice):
    instances = InstanceManager()

class RefusePersonChoice(Choice):
    instances = InstanceManager()
    
    
class ComplaintPhotoPicker(ImagePicker):
    type = StringProperty()
    quizwidget = ObjectProperty()
    
    def on_image_picked(self, filepath):
        
        filepath = self.compress(filepath)
        #existing = AnswerImage.objects.filter()
        logger.info(f'create image {filepath}')
        dbimage, created = AnswerImage.objects.get_or_create(
            type=self.type, 
            answer=self.quizwidget.answer,
            filepath=filepath
        )
        
        #logger.debug(list(AnswerImage.objects.values_list('filepath', flat=True)))
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
        AnswerImage.objects.get(id=cross.parent.dbid).update(
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

В Участковую Избирательную Комиссию {answer.uik}, {region}
От кого: {role} {profile.last_name} {profile.first_name} {profile.middle_name}.
e-mail: {profile.email}

Я, {profile.last_name} {profile.first_name}, находясь в помещении УИК {answer.uik} {date} приблизительно в {answer.time_created.hour} часов стал свидетелем нарушения [TODO: нарушения чего, по каждому инпуту]. Прошу рассмотреть жалобу на заседании комиссии и устранить нарушение. 

Прошу выдать мне заверенную копию решения комиссии.

[если есть] Приложения: Акт, 1 лист.

Дата: {date} Время: ____

{profile.last_name} {profile.first_name} {profile.middle_name}, {role} <Подпись> 
тел.: +7 {profile.phone}
'''

tik_header = '''
Жалоба

В Территориальную Избирательную Комиссию {state.tik.name}, {region}
От кого: {role} {profile.last_name} {profile.first_name} {profile.middle_name}.
e-mail: {profile.email}

Я, {profile.last_name} {profile.first_name}, находясь в помещении УИК {answer.uik} {date} приблизительно в {answer.time_created.hour} часов стал свидетелем нарушения [TODO: нарушения чего, по каждому инпуту]. Составив жалобу, приложенную к данному письму, обратился к {whom} с просьбой принять жалобу и рассмотреть на заседании комиссии для устранения нарушения. 
'''

tik_footer = '''Прошу также рассмотреть мою жалобу по существу и донести решение до Участковой Избирательной Комииссии.

Прошу уведомить меня о принятии решения по телефону +7 {profile.phone}, а также выслать копию решения по электронной почте {profile.email}.

Дата: {date}

{profile.last_name} {profile.first_name} {profile.middle_name}.
'''

refuse_resolve_stub = tik_header + """
Комиссия не стала рассматривать мою жалобу, в связи с чем был составлен акт, приложенный к данному письму.
Прошу признать бездействие Участковой Избирательной Комиссии незаконным. 
""" + tik_footer

refuse_accept_stub = tik_header + """
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

Мы, нижеподписавшиеся, находясь в помещении УИК {answer.uik} {date}, приблизительно в {answer.time_created.hour} часов стали свидетелями того, как {role} {profile.first_name} {profile.last_name} обратился к (секретарю\председателю\...) с просьбой (принять\рассмотреть) жалобу на возможное нарушение.
(Комиссия\председатель\...) (не стала рассматривать\отказалась принять жалобу\отказалась выдать копию решения\...)

Дата: {date} Время: ____

{profile.last_name} {profile.first_name} {profile.middle_name}, {role} <Подпись> тел.: +7 {profile.phone}
<ФИО>, <Статус> <Подпись> <Телефон>
<ФИО>, <Статус> <Подпись> <Телефон>
...
'''

complaint_rules = '''
ФЗ 67 ст.20 

п 4. Комиссии обязаны в пределах своей компетенции рассматривать поступившие к ним в период избирательной кампании обращения о нарушении закона, проводить проверки по этим обращениям и давать лицам, направившим обращения, письменные ответы в пятидневный срок, но не позднее дня, предшествующего дню голосования, а по обращениям, поступившим в день голосования или в день, следующий за днем голосования, — немедленно. Если факты, содержащиеся в обращениях, требуют дополнительной проверки, решения по ним принимаются не позднее чем в десятидневный срок. Если обращение указывает на нарушение закона кандидатом, избирательным объединением, инициативной группой по проведению референдума, эти кандидат, избирательное объединение, инициативная группа по проведению референдума или его (ее) уполномоченные представители должны быть незамедлительно оповещены о поступившем обращении и вправе давать объяснения по существу обращения.

п 5. Комиссии вправе, в том числе в связи с обращениями, указанными в пункте 4 настоящей статьи, обращаться с представлениями о проведении соответствующих проверок и пресечении нарушений закона в правоохранительные органы, органы исполнительной власти. Указанные органы обязаны в пятидневный срок, если представление получено за пять и менее дней до дня голосования, — не позднее дня, предшествующего дню голосования, а если в день голосования или в день, следующий за днем голосования, — немедленно принять меры по пресечению этих нарушений и незамедлительно проинформировать о результатах обратившуюся комиссию. Если факты, содержащиеся в представлении, требуют дополнительной проверки, указанные меры принимаются не позднее чем в десятидневный срок.

---
Практические советы

Жалоба в УИК должна содержать сведения о номере УИК, вашем статусе (наблюдатель, член комиссии и т.д.), вашей фамилии, имени и отчестве, адресе для ответа, дате, времени и месте нарушения, допустившем нарушение лице, указываться суть жалобы (описание нарушения), ссылки на нормы нарушенного законодательства и просительную часть (требования) о вынесении решения по признанию действий (бездействия)  незаконными и совершении определённых действий (принятии решения по существу). В конце жалобы проставляется дата и время написания жалобы, ваша подпись и расшифровка. Жалоба пишется в двух экземплярах. Первый экземпляр жалобы остается у вас, второй подаётся в УИК председателю, заместителю председателя или секретарю УИК. В случае отсутствия указанных лиц жалобу можно подать любому члену УИК с правом решающего голоса. На вашем экземпляре принимающий член УИК должен поставить отметку "принято", указать дату, время, свои фамилию, инициалы и подпись. К жалобе, подаваемой в УИК, прилагаются доказательства (акты, фотоматериалы, видеозаписи). Наличие приложений указавается в жалобе с наименованием прилагаемых документов и количеством листов или с указанием на прилагаемый материальный носитель с файлами (оптический диск, USB-флеш накопитель).
'''

roles = {
    'prg': 'член комиссии с правом решающего голоса УИК {answer.uik}',
    'psg': 'член комиссии с правом совещательного голоса УИК {answer.uik}',
    'nabludatel': 'наблюдатель на УИК {answer.uik}',
    'smi': 'журналист',
    'kandidat': 'кандидат',
    'izbiratel': 'избиратель на УИК {answer.uik}',
    'other': 'избиратель',
}

class Complaint(VBox):
    quizwidget = ObjectProperty()
    tik_text = StringProperty(None, allow_none=True)
    uik_complaint_text = StringProperty(None, allow_none=True)
    complaint_rules = complaint_rules
    
    def refuse_akt_text(self):
        return akt_stub.format(**self.context())
    #answer = ObjectProperty(None, allow_none=True)
    
    
    #def do_layout(self, *args):
        ##import ipdb; ipdb.sset_trace()
        #return super().do_layout(*args)
        
    async def on_event(self, answer):
        #logger.debug(answer, answer.revoked)
        if answer is None:
            self.visible = False
            return
        
        if answer.revoked or not answer.alarm:
            self.visible = False
            return
            
        #print('conmpl1')
        self.visible = True
        self.ids.loader.opacity = 1
        self.ids.uik_complaint_status.choice = ComplaintStatusChoice.instances.get(
            value=answer.uik_complaint_status
        )
        #print('conmpl2')
        if state.get('tik'):
            if answer.uik_complaint_status in ['got_unfair_reply', 'refuse_to_accept', 'refuse_to_resolve']:
                self.ids.tik_complaint.visible = True
                
                if answer.uik_complaint_status == 'refuse_to_accept':
                    self.ids.refuse_person.visible = True
                    
            #print('conmpl3')
            self.ids.refuse_person_status.choice = RefusePersonChoice.instances.get(
                value=answer.refuse_person
            )
            self.toggle_tik(answer.uik_complaint_status)
        self.build_uik_text()
        
        #print('conmpl4')
        await sleep(0.01)
        
        #print('conmpl5')
        self.ids.uik_complaint_images.del_images()
        self.ids.uik_reply_images.del_images()
        
        logger.debug(f'{self.quizwidget.json["label"]}: {answer.images.count()} images for answer {answer.id}')
        for dbimage in answer.images.all():
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
        logger.debug(f'{self.quizwidget.answer.id}, {value}')
        Answer.objects.filter(id=self.quizwidget.answer.id).update(
            uik_complaint_status=value, time_updated=now()
        )
        self.toggle_tik(value)
        
        
    def toggle_tik(self, uik_complaint_status):
        if not state.get('tik'):
            return
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
        Answer.objects.filter(id=self.quizwidget.answer.id).update(
            refuse_person=value
        )
        self.build_tik_text()
        
    def context(self):
        #answer = self.quizwidget.answer
        role = roles.get(self.quizwidget.answer.role)
        if not role:
            # Если роль была Видеонаблюдатель - он не может подавать жалобу.
            # В примерах текстов будем использовать текущую роль.
            role = roles[state.profile.role]
        return dict(
            answer=self.quizwidget.answer,
            date=self.quizwidget.answer.time_created.strftime('%d.%m.%Y'),
            profile=state.profile,
            refuse_person_status=self.ids.refuse_person_status.value or 'член комиссии',
            state=state, 
            whom2 = whom2[self.ids.refuse_person_status.value], 
            whom=whom[self.ids.refuse_person_status.value],
            role=role.format(answer=self.quizwidget.answer),
            region=state.regions.get(self.quizwidget.answer.region).name
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
        #quizwidget.json['example_uik_complaint']
        self.uik_complaint_text = uik_complaint_stub.format(**self.context())
        
            
        
