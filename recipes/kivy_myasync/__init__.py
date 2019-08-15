#import ipdb; ipdb.sset_trace()

from pythonforandroid.recipes.kivy import KivyRecipe



class KivyAsyncRecipe(KivyRecipe):
    version = '1.11.0'
    url = 'https://github.com/Fak3/kivy/archive/f6400.zip'
    name = 'kivy_myasync'

recipe = KivyAsyncRecipe()
