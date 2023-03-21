from pathlib import Path
import clr
AI_VOICE_EDITOR_PATH = Path(r"C:\Program Files\AI\AIVoice\AIVoiceEditor") # AIVoiceEditorまでのパス
AI_TALK_EDITOR_API_DLL_PATH = AI_VOICE_EDITOR_PATH / "AI.Talk.Editor.Api.dll" #dllあるかチェック
clr.AddReference(str(AI_TALK_EDITOR_API_DLL_PATH))
