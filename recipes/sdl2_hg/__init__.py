from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
import sh

#from pythonforandroid.recipes.sdl2 import LibSDL2Recipe


class LibSDL2Recipe(BootstrapNDKRecipe):
    version = "dd9169424181"
    #version = "ab4d52e38c42" # jumps
    #afc8e5d1d992 fails EGL, fixes segfaults
    # 0ef0e4cb7752 segfaults
    # 6fb31043d8a8 segfaults
    # 662cdc7f1dea segfaults
    # 93771c30420b segfaults
    # 82f9397db3e7 introduced segfaults
    # fe136f38ab71 work and jumps
    url = "https://hg.libsdl.org/SDL/archive/{version}.zip"
    #md5sum = None
    name = 'sdl2_hg'

    dir_name = 'SDL'

    depends = ['sdl2_image', 'sdl2_mixer', 'sdl2_ttf']
    
    def should_build(self, arch):
        #input('hit')
        from os.path import exists, join
        libdir = join(
                self.get_build_dir(arch.arch),
                '../..',
                'libs', arch.arch
            )
        libs = [
            'libhidapi.so', 
            'libmain.so', 
            'libSDL2_image.so', 
            'libSDL2_mixer.so', 
            'libSDL2.so', 
            'libSDL2_ttf.so'
        ]
        return not all(exists(join(libdir, x)) for x in libs)
    
    
    
    def get_recipe_env(self,
                       arch=None,
                       with_flags_in_cc=True,
                       with_python=True):
        env = super(LibSDL2Recipe, self).get_recipe_env(
            arch=arch, with_flags_in_cc=with_flags_in_cc,
            with_python=with_python
        )
        env['APP_ALLOW_MISSING_DEPS'] = 'true'
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, "V=1", _env=env)


recipe = LibSDL2Recipe()
