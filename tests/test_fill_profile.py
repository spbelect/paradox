import json
import os
from app_state import state
from asyncio import sleep
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from unittest import TestCase, skip
from unittest.mock import patch, Mock, ANY
import pytest
import pytest_asyncio
import asyncio

from .fixtures import app, mocked_api
from .base import wait_instance, wait_listitem, retry


@pytest.mark.asyncio
async def test_fill_profile(mocked_api, app):
    from paradox import uix
    from paradox.uix.quiz_widgets.base import QuizWidget
    from paradox.uix.confirm import ConfirmModal

    from paradox.models import Answer

    await sleep(0.2)

    await app.click(uix.screens.home.screen.ids.menu_button)

    await sleep(1.2)

    await app.click(uix.sidepanel.ids.region)
    #print(uix.screens.position.screen.ids.region_choices)

    await sleep(1.5)
    # Экран позиции.
    # Кликнуть на список регионов.
    await app.click(uix.screens.position.screen.ids.regions)

    await sleep(0.1)
    # import ipdb; ipdb.sset_trace()
    # Кликнуть на "Лен область"
    await app.click(await retry(uix.screens.position.screen.ids.regions.getchoice, 'ru_47'))

    # await sleep(0.1)
    # Кликнуть "выбрать статус"
    await app.click(uix.screens.position.screen.ids.roles)

    # Кликнуть на "ПРГ"
    await app.click(await retry(uix.screens.position.screen.ids.roles.getchoice, 'prg'))

    # Кликнуть на "Номер УИК"
    await app.click(uix.screens.position.screen.ids.uik)
    # Ввести 1803
    await app.text_input('1803')

    # Кликнуть "Продолжить"
    await app.click(uix.screens.position.screen.ids.next)

    # Экран профиля.
    await app.click(uix.screens.userprofile.screen.ids.first_name)
    await app.text_input('name')
    await app.click(uix.screens.userprofile.screen.ids.last_name)
    await app.text_input('famil')
    await app.click(uix.screens.userprofile.screen.ids.email)
    await app.text_input('email@example.com')
    await app.click(uix.screens.userprofile.screen.ids.phone)
    await app.text_input('9061234567')
    # Кликнуть "Продолжить"
    await app.click(uix.screens.userprofile.screen.ids.next)

    await sleep(1)

    assert [json.loads(x.request.content) for x in mocked_api.routes['post_position'].calls] == [
        {"uik": 1803, "region": "ru_47", "country": "ru", "role": "prg", "app_id": state.app_id},
    ]

    assert state.profile.as_dict() == {
        "last_name": 'famil',
        "email": 'email@example.com',
        "phone": '9061234567',
        'first_name': '',
        'middle_name': '',
        'telegram': ''
    }

