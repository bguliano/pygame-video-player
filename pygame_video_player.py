import enum
import os
import sys
from dataclasses import dataclass
from typing import Tuple, Optional, Union

import cv2
import moviepy.editor
import pygame

pygame.init()
pygame.mixer.init()


class ResizeMethod(enum.IntEnum):
    ALL_AT_ONCE = 0  # good
    FRAME_BY_FRAME = 1  # better
    CV2 = 2  # best


class CV2Interpolation(enum.IntEnum):  # easier than searching the docs for all the possible values
    INTER_AREA = cv2.INTER_AREA
    INTER_BITS = cv2.INTER_BITS
    INTER_BITS2 = cv2.INTER_BITS2
    INTER_CUBIC = cv2.INTER_CUBIC
    INTER_LANCZOS4 = cv2.INTER_LANCZOS4
    INTER_LINEAR = cv2.INTER_LINEAR
    INTER_LINEAR_EXACT = cv2.INTER_LINEAR_EXACT
    INTER_NEAREST = cv2.INTER_NEAREST


@dataclass
class VideoOptions:
    show_fps: bool = False
    show_target_fps: bool = False
    show_resolution: bool = False
    show_target_resolution: bool = False
    text_antialiasing: bool = True
    resize_method: ResizeMethod = ResizeMethod.CV2
    cv2_interpolation: CV2Interpolation = CV2Interpolation.INTER_LINEAR
    fullscreen: bool = False
    lock_fps: bool = False
    # tick_busy_loop is more accurate, but consumes more CPU
    tick_func: Union[pygame.Clock.tick_busy_loop, pygame.Clock.tick] = pygame.Clock.tick_busy_loop


class VideoPlayer:
    def __init__(self, filename: str, resolution: Tuple[int, int], video_options: Optional[VideoOptions] = None):
        self.options = video_options or VideoOptions()

        window_flag = pygame.FULLSCREEN if self.options.fullscreen else pygame.RESIZABLE
        self.window = pygame.display.set_mode(resolution, window_flag)

        rect = pygame.Rect(0, 0, *resolution)
        self._image = pygame.Surface(rect.size, pygame.HWSURFACE)
        self._rect = self._image.get_rect()
        self._rect.x = rect.x
        self._rect.y = rect.y

        self._max_res_video = moviepy.editor.VideoFileClip(filename)

        if self.options.resize_method == ResizeMethod.ALL_AT_ONCE:
            self._video = self._max_res_video.resize(self._rect.size)
        elif self.options.resize_method == ResizeMethod.FRAME_BY_FRAME:
            self._video = self._max_res_video
        elif self.options.resize_method == ResizeMethod.CV2:
            self._video = self._max_res_video

        audio_filename = os.path.splitext(filename)[0] + '.wav'
        if not os.path.exists(audio_filename):
            self._max_res_video.audio.write_audiofile(audio_filename)
        self._pygame_sound = pygame.mixer.Sound(file=audio_filename)

        self.playing = False
        self._start_time = 0
        self._video_delay = 250

    def play(self):
        # init video and audio tracks
        self._start_time = pygame.time.get_ticks()
        self._pygame_sound.play()
        self.playing = True

        fps_clock = pygame.Clock()
        fps_font = pygame.font.SysFont("Arial", 18, bold=True)
        res_font = pygame.font.SysFont("Arial", 18, bold=True)

        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False
                elif event.type == pygame.VIDEORESIZE:
                    self._handle_resize(event.size)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.playing = False

            # handle getting a new image and showing it on screen
            self._render_frame()
            self.window.blit(self._image, self._rect)

            # show fps
            if self.options.show_fps:
                fps = str(round(fps_clock.get_fps()))
                if self.options.show_target_fps:
                    fps += f' ({round(self._video.fps)})'
                fps_t = fps_font.render(fps, self.options.text_antialiasing, pygame.Color('white'))

                # calculate 1% padding
                fps_t_rect = fps_t.get_rect()
                fps_t_rect.x = self._rect.width * 0.01
                fps_t_rect.y = self._rect.height * 0.01

                self.window.blit(fps_t, fps_t_rect)

            # show resolution
            if self.options.show_resolution:
                resolution = f'{self._rect.width}x{self._rect.height}'
                if self.options.show_target_resolution:
                    resolution += f' ({self._max_res_video.w}x{self._max_res_video.h})'
                res_t = res_font.render(resolution, self.options.text_antialiasing, pygame.Color('white'))

                # calculate 1% padding
                res_t_rect = res_t.get_rect()
                res_t_rect.right = self._rect.width - (self._rect.width * 0.01)
                res_t_rect.y = self._rect.height * 0.01

                self.window.blit(res_t, res_t_rect)

            # finally update screen
            pygame.display.flip()

            # tick to update framerate correctly
            self.options.tick_func(fps_clock, self._video.fps if self.options.lock_fps else 0)

    def _handle_resize(self, new_size: Tuple[int, int]):
        self._rect.size = new_size

        if self.options.resize_method == ResizeMethod.ALL_AT_ONCE:
            self._video = self._max_res_video.resize(self._rect.size)

    def _render_frame(self):
        current_time = pygame.time.get_ticks() - (self._start_time + self._video_delay)
        current_seconds = current_time / 1000

        self.playing = self.playing and self._video.is_playing(max(0.0, current_seconds))

        if self.playing:
            if self.options.resize_method == ResizeMethod.ALL_AT_ONCE:
                raw_image = self._video.get_frame(current_seconds)  # video has already been resized
            elif self.options.resize_method == ResizeMethod.FRAME_BY_FRAME:
                image_clip = self._video.to_ImageClip(current_seconds).resize(self._rect.size)
                raw_image = image_clip.get_frame(0)
            elif self.options.resize_method == ResizeMethod.CV2:
                numpy_image = self._video.get_frame(current_seconds)
                raw_image = cv2.resize(numpy_image, dsize=self._rect.size, interpolation=self.options.cv2_interpolation)

            self._image = pygame.image.frombuffer(raw_image, self._rect.size, 'RGB')


if __name__ == '__main__':
    options = VideoOptions(
        show_fps=True,
        show_target_fps=True,
        show_resolution=True,
        show_target_resolution=True
    )
    vid = VideoPlayer('/Users/bguliano/Downloads/video2.mp4', (1920, 1200), options)
    vid.play()
    pygame.quit()
    sys.exit(0)
