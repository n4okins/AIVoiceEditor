from . import config
from AI.Talk.Editor.Api import TtsControl # 必ずconfigをインポートしてから，あとエラー出るけど気にしない

from dataclasses import dataclass, asdict
from enum import Enum
import json
from typing import Callable, Iterable
import time

__all__ = [
    "MasterControl", "AIVoiceActor"
]


class _HostStatus(Enum):
    NotRunning = 0
    NotConnected = 1
    Idle = 2
    Busy = 3


class _TextEditMode(Enum):
    Text = 0
    List = 1


@dataclass
class MasterControl:
    """
    Volume: float = 1.0: 音量
    Speed: float = 1.0: 話速
    Pitch: float = 1.0: 高さ
    PitchRange: float = 1.0: 抑揚
    MiddlePause: int = 150: 短ポーズ [ms]
    LongPause: int = 370: 長ポーズ [ms]
    SentencePause: int = 800: 文末ポーズ [ms]
    """
    Volume: float = 1.0
    Speed: float = 1.0
    Pitch: float = 1.0
    PitchRange: float = 1.0
    MiddlePause: int = 150
    LongPause: int = 370
    SentencePause: int = 800


@dataclass
class _TtsControl:
    """
    https://aivoice.jp/manual/editor/API/html/bbcdfea3-b7a8-4cdf-1479-15fa48cef15e.htm
    """
    CurrentVoicePresetName: str
    IsInitialized: bool
    MasterControl: str
    Status: _HostStatus
    Text: str
    Version: str
    VoiceNames: Iterable[str]
    VoicePresetNames: Iterable[str]

    Connect: Callable[[], None]
    Disconnect: Callable[[], None]
    GetAvailableHostNames: Callable[[], Iterable[str]]
    GetPlayTime: Callable[[], int]
    GetListVoicePreset: Callable[[], Iterable[str]]
    GetVoicePreset: Callable[[str], str]
    Play: Callable
    Initialize: Callable[[str], str]
    StartHost: Callable[[], None]


class AIVoiceActor:
    def __init__(self):
        self.connect_control: _TtsControl = TtsControl()

        self.host_name = self.connect_control.GetAvailableHostNames()[0]
        assert self.host_name, "HostName not found."

        self._initialize()
        self.connect()

        self.init_master_control()

        if self.connect_control.Status == _HostStatus.NotRunning:
            self.connect_control.StartHost()

    def _initialize(self) -> str:
        print(f"=== Initializing ===")
        return self.connect_control.Initialize(self.host_name)

    def init_master_control(self):
        init_master_control = MasterControl()
        self.master_control = init_master_control

    def connect(self):
        self.connect_control.Connect()
        print(
            f"=== Connecting === \n-> {'Host':<8s}: {self.host_name} \n-> {'Version':<8s}: {self.connect_control.Version}")

    @property
    def text(self):
        return self.connect_control.Text

    @text.setter
    def text(self, input_text: str):
        disp_text = input_text if len(input_text) < 20 else input_text[:8] + " ... " + input_text[-8:]
        print(f"=== Update Text: {disp_text} (length: {len(input_text)})")
        self.connect_control.Text = input_text

    def play(self, after_blank=500, estimate=True):

        if estimate:
            estimate_time = (self.connect_control.GetPlayTime() + after_blank) / 1000
            print(f"=== Estimate time: {estimate_time:.3f} [s]\n=== Playing ===")

        self.connect_control.Play()

        if estimate:
            time.sleep(estimate_time)
        print(f"=== Finished === ")

    @property
    def master_control(self) -> MasterControl:
        return MasterControl(**dict(json.loads(self.connect_control.MasterControl)))

    @master_control.setter
    def master_control(self, master_control_data: MasterControl):
        print(f"=== Update Master Control === \n-> {asdict(master_control_data)}")
        self.connect_control.MasterControl = json.dumps(asdict(master_control_data))

    def disconnect(self):
        print(f"=== Disconnected  === \n-> {'Host':<8s}: {self.host_name}")
        self.connect_control.Disconnect()

    def __delete__(self, instance):
        self.disconnect()


if __name__ == "__main__":
    actor = AIVoiceActor()
    actor.text = "Pythonからおとどけ"
    actor.play()
    actor.master_control = MasterControl(Speed=1.75, Pitch=1.1, PitchRange=1.2)
    actor.play()
    actor.disconnect()
