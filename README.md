# pygame-video-player
Uses a combination of pygame and moviepy (based on ffmpeg) to display videos in Python

***Note: This is a very early implementation of this concept, designed to just be a test at the moment. It renders one pygame window and the video takes up the entire window. This window can be resized, but the video's aspect ratio cannot be preserved. The play() method is blocking, so it can't be used in an existing pygame loop.***

## Future features:
 - video controls (pause, play, stop, load)
 - non-blocking play method that instead can operate in an existing pygame event loop
 - `preserve_aspect_ratio` is a `VideoOptions` attribute to preserve the video's original aspect ratio when resizing
 - `self.video_delay` is now a `VideoOptions` attribute
 - `cv2` library is not required unless you want to use `VideoOptions.resize_method = ResizeMethod.CV2`
 - documentation and docstrings

## Some background
The idea to create this module came after searching for hours for a very simple, easy-to-use video player in pure Python. I tested several libraries, example code, and StackOverflow recommendations, but nothing was quite what I needed, or rendered very slowly.

So, I decided to create my own. `pygame` seemed like the way to go because it was already designed to render things on a screen (like frames of a video), it had audio support built-in, and it allowed for control over the fps of the display. The `moviepy` library allowed for grabbing frames of a video file at a certain time, so this method used in conjunction with `pygame`'s time counting allowed for accurate playback and synchronization with the audio.

Resizing was a bit more of a struggle, as the builtin `moviepy` resize algorithm was slow, so I had to look for others before stumbling across `cv2.resize`, which turned out to be significantly faster than using a `moviepy` alternative. Of course, this adds another package that needs to be imported, which detracts from the goal of this project being as simple and lightweight as possible, so making `cv2` an optional import will be added as a future feature.

Overall, this project adds the ability for Python to display videos natively, simply by rendering frames of the video within a set (or unlocked using `VideoOptions.lock_fps = False`) framerate, while also simultaneously synchronizing the audio track.

Other `VideoOptions` attributes exist to customize playback, including `fullscreen`, `show_fps`, etc. Check the source code to see them all. Eventually, a list of all the options will be provided with descriptions in this README.
