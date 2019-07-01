#import ipdb; ipdb.sset_trace()

from pythonforandroid.recipes.kivy import KivyRecipe



class KivyTestRecipe(KivyRecipe):
    version = '1.11.0'
    url = 'https://github.com/kivy/kivy/archive/37c0b303a750ff9c0dcd23fb7e290298186a4e0a.zip'
    name = 'kivy_test'

recipe = KivyTestRecipe()
