import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sdl2.sdlmixer import *

class SoundMixer:
    music = None
    sfx = {}
    channels = {}

    def __init__(self, uglix):
        # save the UglixTools()
        self.uglix = uglix

        flags = MIX_INIT_MP3 | MIX_INIT_OGG
        if Mix_Init(flags) != flags:
            raise ValueError("SDL2 ne gère pas les mp3 ou les ogg ?!?")
        if Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 1024) == -1:
            raise ValueError("Mix_OpenAudio: {}".format(Mix_GetError()))

    def load_sfx(self, path, key):
        sfx = Mix_LoadWAV(str(path).encode())
        if sfx is None:
            raise ValueError("Mix_LoadWAV")
        self.sfx[key] = sfx

    def play_sfx(self, filename, target_channel=-1, loops=0, fadein=None):
        """
        play loops time (-1 == +oo)
        channel == -1 ====> first available channel (not played if no channels available)
        fadein in ms or None
        """
        if filename not in self.sfx:
            path = self.uglix.ensure_file('sfx/' + filename, filename, static=True)
            self.load_sfx(path, filename)
        sfx = self.sfx[filename]
        if fadein:
            channel = Mix_FadeInChannel(target_channel, sfx, loops, fadein)
        else:
            channel = Mix_PlayChannel(target_channel, sfx, loops)
        if channel == -1:
            print("warning, no available sound channel")
        if loops != 0:
            self.channels[filename] = channel
    
    def fadeout_sfx(self, filename, fadeout):    
        if filename not in self.channels:
            return
        channel = self.channels[filename]
        del self.channels[filename]
        Mix_FadeOutChannel(channel, fadeout)

    def silence_sfx(self, filename):
        if filename is None:
            Mix_HaltChannel(-1)
        if filename not in self.channel:
            return
        channel = self.channels[filename]
        del self.channels[filename]
        Mix_HaltChannel(channel, fadeout)

    def stop_music(self):
        if self.music is not None:
            Mix_FreeMusic(self.music)      # this releases resources
            self.music = None

    def play_music(self, filename, loops=-1):
        """
        loops = 0  ===> play once
        loops = -1 ===> play ad libitum
        """
        path = self.uglix.ensure_file('music/' + filename, filename, static=True)
        self.stop_music()
        if not path:
            return
        self.music = Mix_LoadMUS(str(path).encode())  # fonctionne avec les positions LOOPSTART et LOOPEND exprimées en #samples
        if self.music is None:
            raise ValueError("Mix_LoadMus")
        if Mix_PlayMusic(self.music, -1) == -1:
            raise ValueError("Mix_PlayMusic: {}".format(Mix_GetError()))

