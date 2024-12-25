#import ipdb; ipdb.sset_trace()

from pythonforandroid.recipes.kivy import KivyRecipe



class Kivy231Recipe(KivyRecipe):
    version = '2.3.1'
    url = 'https://github.com/kivy/kivy/archive/refs/heads/devel-2.3.x.zip'
    name = 'kivy_2.3.1'

recipe = Kivy231Recipe()
