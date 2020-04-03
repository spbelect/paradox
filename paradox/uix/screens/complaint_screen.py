# -*- coding: utf-8 -*-

from __future__ import unicode_literals

#from os.path import exists
from datetime import date
import traceback


from app_state import state, on
from django.utils.timezone import now
from kivy.core.window import Window
from kivy.app import App
#from kivy.garden.anchoredscrollview import AnchoredScrollView
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard

from kivy.utils import platform
from loguru import logger

from label import Label
from button import Button
from paradox import uix
from paradox import utils
from paradox.models import AnswerImage, Answer, Campaign
from paradox.uix import float_message
from paradox.uix.choices import Choice
from paradox.uix.frozen_editor import FrozenEditor
from paradox.uix.imagepicker import ImagePicker


Builder.load_string('''
#:include constants.kv

#:set compaint_spacing dp(50)

<ComplaintSpacerLarge@Widget>:
    size_hint_y: None
    height: dp(40)

<ComplaintSpacerSmall@Widget>:
    size_hint_y: None
    height: dp(15)
    
    
<BlueButton@Button>:
    text: 'зачем писать жалобу'
    color: lightblue
    font_size: dp(20)
                
<ComplaintScreen>:
    ScrollView:
        id: scrollview

        VBox:
            #padding: 0
            #spacing: 0
            
            Label:
                text: f"{root.answer.question.label}" if root.answer else ''
                height: self.texture_size[1]  # Grow height to fit all text
            Label:
                text: f"[color=#882311]{root.answer.humanized_value}[/color]" if root.answer else ''
                #height: font1
                markup: True
                
            ComplaintSpacerLarge:
            
            Label:
                text: "ОБЖАЛОВАНИЕ В УИК"
                font_size: dp(24)
                height: self.font_size + dp(6)
                color: white
                background_color: wheat4
                    
            ComplaintSpacerSmall:
            
            BlueButton:
                text: 'зачем писать жалобу'
                content: open('paradox/zachem_pisat_jalobu.txt').read()
                on_release: uix.screenmgr.show_handbook('ЗАЧЕМ НУЖНО ОБЖАЛОВАНИЕ', self.content)
            
            ComplaintSpacerSmall:
            
            BlueButton:
                text: 'правила обжалования'
                content: open('paradox/complaint_rules.txt').read()
                on_release: uix.screenmgr.show_handbook('ПРАВИЛА ОБЖАЛОВАНИЯ', self.content)

            ComplaintSpacerSmall:
            
            BlueButton:
                text: 'пример жалобы'
                on_release: 
                    uix.screenmgr.show_handbook(root.answer.question.label, root.uik_complaint_text)
                
            ComplaintSpacerLarge:
            
            Label:
                #height: self.font_size + dp(30)  # 
                font_size: dp(20)
                height: self.font_size
                text: 'сфотографируйте жалобу и акт'
                color: lightgray if uik_complaint_images.ids.images.children else black
                #text_size: self.width, None
                #halign: 'left'
                
            ComplaintPhotoPicker:
                id: uik_complaint_images
                type: 'uik_complaint'
                answer: root.answer
                compress_quality: 40
                #on_image_picked: root.on_image_picked(filepath)
                
            ComplaintSpacerLarge:
            
            Label:
                font_size: dp(20)
                height: self.font_size
                text: 'статус жалобы'if uik_complaint_status.value else 'укажите статус жалобы' 
                #text_size: self.width, None
                color: black if uik_complaint_status.value in (None, 'none') else lightgray
                
            ChoicePicker:
                id: uik_complaint_status
                height: self.font_size + dp(20)
                font_size: dp(20)
                #height: self.texture_size[1]
                modal_header: 'Статус жалобы'
                text: 'выберите статус'
                text_size: self.width, None
                #halign: 'left'
                on_text: self.color = black
                padding: 0, 0
                on_new_pick: root.on_uik_complaint_status_input(self.value)
                size_hint_y: None
                        
                Choice:
                    value: 'none'
                    text: 'не подавалась'
                Choice:
                    value: 'refuse_to_accept'
                    text: 'отказ принять жалобу'
                Choice:
                    value: 'refuse_to_resolve'
                    text: 'отказ рассмотрения жалобы'
                    short_text: 'отказ рассмотрения'
                Choice:
                    value: 'waiting_reply'
                    text: 'ожидание решения комиссии'
                    short_text: 'ожидание решения'
                Choice:
                    value: 'got_unfair_reply'
                    text: 'получено неудовлетворительное решение'
                    short_text: 'получено неуд. решение'
                Choice:
                    value: 'got_fair_reply'
                    text: 'получено удовлетворительное решение'
                    short_text: 'получено удовл. решение'

            VBox:
                padding: 0
                visible: uik_complaint_status.value in ['got_fair_reply', 'got_unfair_reply']
                
                ComplaintSpacerLarge:
            
                Label:
                    font_size: dp(20)
                    height: self.font_size
                    text: 'сфотографируйте решение'
                    color: lightgray if uik_reply_images.ids.images.children else black
                    #halign: 'left'
                    
                ComplaintPhotoPicker:
                    id: uik_reply_images
                    type: 'uik_reply'
                    answer: root.answer
                    compress_quality: 40
                    
            ComplaintSpacerLarge:
            
                    
            #############################################
            # ОБЖАЛОВАНИЕ В ТИК
            #############################################
            
            VBox:
                visible: not state.tik or not state.tik.email
                
                Label:
                    height: self.font_size + compaint_spacing
                    font_size: dp(14)
                    color: lightgray
                    text: 'У нас нет email адреса ТИК для УИК %s' % state.uik
                    
            VBox:
                id: tik_block
                #padding: 0, dp(40), 0, 0
                padding: 0
                visible: False
                    
                ComplaintSpacerLarge:
            
                Label:
                    text: "ОБЖАЛОВАНИЕ В ТИК"
                    font_size: dp(24)
                    height: self.font_size + dp(6)
                    color: white
                    background_color: wheat4
                    
                VBox:
                    # Блок акта об отказе. Показан если статус == "отказ" принять или рассмотреть жалобу
                    id: refuse_akt_block
                    visible: bool(uik_complaint_status.value in ['refuse_to_accept', 'refuse_to_resolve'])
                    padding: 0
                                
                    ComplaintSpacerSmall:
                        
                    BlueButton:
                        text: 'составьте акт об отказе'
                        on_release: uix.screenmgr.show_handbook('Составьте акт', root.akt_stub.format(**root.context()))

                    ComplaintSpacerSmall:
                    
                    Label:
                        font_size: dp(20)
                        height: self.font_size
                        text: 'сфотографируйте акт'
                        color: lightgray if refuse_akt_images.ids.images.children else black
                        #text_size: self.width, None
                        #halign: 'left'
                        
                    ComplaintPhotoPicker:
                        id: refuse_akt_images
                        type: 'tik_complaint'
                        answer: root.answer
                        compress_quality: 40
                        #on_image_picked: root.on_image_picked(filepath)
                    
                VBox:
                    # Блок "Кто отказал принять жалобу". Показан если статус == "отказ принять".
                    id: refuse_person_block
                    visible: bool(uik_complaint_status.value == 'refuse_to_accept')
                    #padding: 0, dp(1), 0, 0
                    spacing: 0
                                    
                    ComplaintSpacerLarge:

                    Label:
                        font_size: dp(20)
                        height: self.font_size
                        text: 'кому подавали жалобу' if refuse_person.value else 'Укажите кому подавали жалобу'
                        color: lightgray if refuse_person.value else black
                        
                    ChoicePicker:
                        id: refuse_person
                        height: self.font_size + dp(20)
                        font_size: dp(20)
                        modal_header: 'Выберите статус'
                        text: 'выберите статус'
                        on_text: self.color = black
                        #padding: 0, 0
                        on_new_pick: root.on_refuse_person(self.value)
                                
                        Choice:
                            value: 'член комиссии'
                            text: 'член комиссии (или неизвестно)'
                            short_text: 'член комиссии'
                        Choice:
                            value: 'председатель'
                            text: 'председатель'
                        Choice:
                            value: 'зам. председателя'
                            text: 'зам. председателя'
                        Choice:
                            value: 'секретарь'
                            text: 'секретарь'
                    
                ComplaintSpacerLarge:

                Label:
                    id: tik_send_status
                    color: wheat4
                    font_size: dp(20)
                    height: self.font_size
                    
                ComplaintSpacerSmall:
                
                FrozenEditor:
                    id: tik_text_editor
                    text: getattr(root.answer, 'tik_complaint_text', None) or root.generated_tik_text
                    #text: root.generated_tik_text
                    on_save: root.on_tik_text_input
                    
                Button:
                    text: 'Отправить на проверку'
                    disabled: tik_text_editor.disabled or not tik_text_editor.frozen or not state.tik.email
                    # TODO: отправить сразу если нет координаторов которые готовы проверить.
                    on_release: root.on_send_pressed()
                    color: teal
                    disabled_color: lightgray  # Some kivy bug requires to set this explicitly
                    
                Label:
                    id: recipients
                    font_size: dp(16)
                    color: lightgray
                    split_str: ' '
                    height: self.texture_size[1]  # Grow height to fit all text
                    
                Label:
                    text: 'Оператор проверит текст жалобы и может отправить email в тик, если нет ошибок. Укажите свой telegram адрес в профиле, чтобы оператор и представитель ТИК мог с вами связаться.'
                    font_size: dp(16)
                    color: lightgray
                    # TODO: отправить сразу если нет координаторов которые готовы проверить.
                    split_str: ' '
                    height: self.texture_size[1]  # Grow height to fit all text
                    
            ComplaintSpacerLarge:
            
            Button:
                text: '< Назад'
                on_press: root.manager.pop_screen()
                #halign: 'left'
                #text_size: self.size
                #size: dp(200), dp(30)
                
                height: dp(30)
                width: self.texture_size[0]
                
                text_size: None, self.height
                
                size_hint: None, None
                #width: dp(150)
                background_color: white
                color: teal
                
            ComplaintSpacerSmall:
''')

    
class ComplaintPhotoPicker(ImagePicker):
    type = StringProperty()
    answer = ObjectProperty()
    
    def on_image_picked(self, filepath):
        
        filepath = self.compress(filepath)
        #existing = AnswerImage.objects.filter()
        logger.info(f'create image {filepath}')
        dbimage, created = AnswerImage.objects.get_or_create(
            type=self.type, answer=self.answer, filepath=filepath
        )
        
        #logger.debug(list(AnswerImage.objects.values_list('filepath', flat=True)))
        if dbimage.deleted:
            logger.debug('Undelete previously deleted image.')
            dbimage.update(deleted=False, time_updated=now())
            uxitem = self.add_image(filepath)
            uxitem.dbid = dbimage.id
        elif created:
            uxitem = self.add_image(filepath)
            uxitem.dbid = dbimage.id
        
    def on_cross_click(self, cross):
        super().on_cross_click(cross)
        AnswerImage.objects.get(id=cross.parent.dbid).update(
            deleted=True, time_updated=now()
        )


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

tik_header = '''Жалоба

В Территориальную Избирательную Комиссию {state.tik.name}, {region}
От кого: {role} {profile.last_name} {profile.first_name} {profile.middle_name}.
e-mail: {profile.email}

Я, {profile.last_name} {profile.first_name}, находясь в помещении УИК {answer.uik} {date} приблизительно в {answer.time_created.hour} часов стал свидетелем нарушения [TODO: нарушения чего, по каждому инпуту]. Составив жалобу, приложенную к данному письму, обратился к {komu} с просьбой принять жалобу и рассмотреть на заседании комиссии для устранения нарушения. 
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
{refuse_person} отказал мне в принятии жалобы, в связи с чем был составлен акт, приложенный к данному письму.
Прошу признать бездействие {kogo} незаконным.
""" + tik_footer

tik_complaint_stub = tik_header + """
Комиссия вынесла решение, противоречащее законодательству. Нарушение не устранено.
Прошу признать решение Участковой Избирательной Комииссии незаконным.
""" + tik_footer


akt_stub = '''
Попросите свидетелей поставить подписи и оставить телефон под актом. Телефон желательно оставить, так как в вышестоящей комиссии могут связаться со свидетелями для подтверждения\уточнения произошедшего.

Примерный текст:

Акт

Мы, нижеподписавшиеся, находясь в помещении УИК {answer.uik} {date}, приблизительно в {answer.time_created.hour} часов стали свидетелями того, как наблюдатель\член комиссии\... {profile.first_name} {profile.last_name} обратился к (секретарю\председателю\...) с просьбой (принять\рассмотреть) жалобу на возможное нарушение.
(Комиссия\председатель\...) (не стала рассматривать\отказалась принять жалобу\отказалась выдать копию решения\...)

Дата: {date} Время: ____

{profile.last_name} {profile.first_name} {profile.middle_name}, статус (наблюдатель\член комиссии\...) <Подпись> тел.: +7 {profile.phone}
<ФИО>, <Статус> <Подпись> <Телефон>
<ФИО>, <Статус> <Подпись> <Телефон>
...
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

class ComplaintScreen(Screen):
    #answer = ObjectProperty(Answer(question_id='dummy'))
    answer = ObjectProperty(None, allow_none=True)
    generated_tik_text = StringProperty('')
    uik_complaint_text = StringProperty(None, allow_none=True)
    akt_stub = akt_stub
        
    def show(self, answer):
        self.answer = answer
        vote_dates = Campaign.objects.positional().current().values_list('vote_date', flat=True)
        #today = now().date()
        if now().date() in list(vote_dates):
            self.ids.recipients.text = f'После проверки оператором email будет отправлен в ТИК по адресу {state.tik.email}. '\
                f'Также копия будет отправлена вам на адрес {state.profile.email}'
        else:
            self.ids.recipients.text = f'Сейчас нет активных координаторов и проходящих выборов '\
                'в вашем регионе. Письмо не будет отправлено в ТИК.'
            
        if not answer.tik_complaint_status or answer.tik_complaint_status == 'none':
            self.ids.tik_send_status.text = 'ПРОВЕРЬТЕ ТЕКСТ ЖАЛОБЫ'
            self.ids.tik_text_editor.disabled = False
        elif answer.tik_complaint_status == 'sending_to_moderator':
            self.ids.tik_send_status.text = 'ЗАПРОС ОТПРАВЛЯЕТСЯ'
            self.ids.tik_text_editor.disabled = True
        elif answer.tik_complaint_status == 'moderating':
            self.ids.tik_send_status.text = 'ЗАПРОС ОТПРАВЛЕН'
            self.ids.tik_text_editor.disabled = True
        else:
            raise Exception(f"Unknown answer.tik_complaint_status {answer.tik_complaint_status}")
        
        self.ids.uik_complaint_status.setchoice(answer.uik_complaint_status)
        
        if state.tik:
            if answer.uik_complaint_status in ['got_unfair_reply', 'refuse_to_accept', 'refuse_to_resolve']:
                self.ids.tik_block.visible = True
                
                if answer.uik_complaint_status == 'refuse_to_accept':
                    self.ids.refuse_person_block.visible = True
                    
            self.ids.refuse_person.setchoice(answer.refuse_person)
            self.set_tik_block_visibility(answer.uik_complaint_status)
        self.build_uik_text()
        
        self.ids.uik_complaint_images.del_images()
        self.ids.uik_reply_images.del_images()
        
        logger.debug(f'{self.answer.question.label}: {answer.images.count()} images for answer {answer.id}')
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
        
    
    def on_uik_complaint_status_input(self, value):
        """ 
        
        """
        self.answer.update(uik_complaint_status=value, time_updated=now())
        self.ids.scrollview.scroll_to(self.ids.uik_complaint_status)
        
        # Если запрос в ТИК уже был отправлен, позволить еще раз отредактировать 
        # и отправить. 
        self.ids.tik_send_status.text = 'ПРОВЕРЬТЕ ТЕКСТ ЖАЛОБЫ'
        self.ids.tik_text_editor.disabled = False
        self.set_tik_block_visibility(uik_complaint_status=value)
        
        
    def set_tik_block_visibility(self, uik_complaint_status):
        """
        В зависимости от статуса обжалования в УИК, показать или нет блок обжалования в 
        ТИК, и блок акта об отказе.
        """
        if not state.tik:
            return
        
        refuse = ['refuse_to_accept', 'refuse_to_resolve']
        if uik_complaint_status not in ['got_unfair_reply'] + refuse:
            self.ids.tik_block.visible = False
            return
        
        if uik_complaint_status in refuse:
            # Составьте акт об отказе.
            self.ids.refuse_akt_block.visible = True
        else:
            self.ids.refuse_akt_block.visible = False
            
        self.ids.tik_block.visible = True
        self.build_tik_text()
        
        
    def on_refuse_person(self, value):
        self.answer.update(refuse_person=value)
        self.build_tik_text()
        
    def context(self):
        komu = {
            None: 'члену комиссии',
            'член комиссии': 'члену комиссии',
            'председатель': 'председателю',
            'зам. председателя': 'заместителю председателя',
            'секретарь': 'секретарю'
        }

        kogo = {
            None: 'члена комиссии',
            'член комиссии': 'члена комиссии',
            'председатель': 'председателя',
            'зам. председателя': 'заместителя председателя',
            'секретарь': 'секретаря'
        }
        
        role = roles.get(self.answer.role)

        if not role:
            # Если роль была Видеонаблюдатель - он не может подавать жалобу.
            # В примерах текстов будем использовать текущую роль.
            role = roles[state.profile.role]
        return dict(
            answer = self.answer,
            date = self.answer.time_created.strftime('%d.%m.%Y'),
            profile = state.profile,
            refuse_person = self.answer.refuse_person or 'член комиссии',
            state = state, 
            kogo = kogo[self.answer.refuse_person], 
            komu = komu[self.answer.refuse_person],
            role = role.format(answer=self.answer),
            region = state.regions.get(self.answer.region).name
        )
    
    @on('state.profile')
    def build_tik_text(self):
        if not self.answer:
            return
        
        if self.answer.tik_complaint_text:
            # Юзер уже отредактировал текст, не будем его изменять
            return
        
        if self.ids.uik_complaint_status.value == 'refuse_to_accept':
            self.generated_tik_text = refuse_accept_stub.format(**self.context())
        elif self.ids.uik_complaint_status.value == 'refuse_to_resolve':
            self.generated_tik_text = refuse_resolve_stub.format(**self.context())
        else:
            # 'got_unfair_reply'
            self.generated_tik_text = tik_complaint_stub.format(**self.context())
        #logger.debug(self.generated_tik_text)

    @on('state.profile')
    def build_uik_text(self):
        if not self.answer:
            return
        self.uik_complaint_text = uik_complaint_stub.format(**self.context())
        
        
    def on_tik_text_input(self, text):
        if not text == self.generated_tik_text:
            # Юзер изменил текст
            self.answer.update(tik_complaint_text=self.ids.tik_text_editor.text)
            
    @utils.asynced
    async def on_send_pressed(self):
        if not self.answer.images.exists():
            msg = 'Рекомендуется приложить фото жалобы. Действительно отправить письмо без приложений?'
            if not await uix.confirm.yesno(msg):
                return
        
        text = self.answer.tik_complaint_text or self.generated_tik_text
        if 'TODO' in text:
            msg = 'Рекомендуется указать в жалобе на конкретное нарушение. Действительно отправить письмо?'
            if not await uix.confirm.yesno(msg):
                return
            
        self.answer.update(
            tik_complaint_status='sending_to_moderator',
            tik_complaint_text=text,
            time_updated=now()
        )
        uix.float_message.show('Запрос отправляется')
        self.ids.tik_send_status.text = 'ЗАПРОС ОТПРАВЛЯЕТСЯ'
        self.ids.tik_text_editor.disabled = True
        
