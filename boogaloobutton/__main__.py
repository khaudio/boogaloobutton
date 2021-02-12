from boogaloobutton import *

if __name__ == '__main__':
    with Rocker('./audio_files', b'letsrock', 54045) as rocker:
        rocker.run()
