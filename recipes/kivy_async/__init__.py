#import ipdb; ipdb.sset_trace()

from pythonforandroid.recipes.kivy import KivyRecipe



class KivyAsyncRecipe(KivyRecipe):
    version = '1.11.0'
    url = 'https://github.com/matham/kivy/archive/async-support.zip'
    name = 'kivy_async'

recipe = KivyAsyncRecipe()
