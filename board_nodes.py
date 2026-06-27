# -*- coding: utf-8 -*-
import json, os, time, subprocess, threading, tempfile
from datetime import datetime
from bt_engine import TreeNode, NodeStatus, ActionNode, ConditionNode, AsyncActionNode

class CheckTimeCondition(ConditionNode):
    def __init__(self, name="CheckTime"): super().__init__(name)
    def execute(self) -> NodeStatus:
        ts = self.get_input("reminder_trigger_time", "")
        if not ts: return NodeStatus.FAILURE
        try:
            if datetime.now() >= datetime.fromisoformat(ts): return NodeStatus.SUCCESS
        except: pass
        return NodeStatus.FAILURE

class BuildTtsText(ActionNode):
    def __init__(self, name="BuildTtsText"): super().__init__(name)
    def execute(self) -> NodeStatus:
        title = self.get_input("reminder_title", "reminder")
        content = self.get_input("reminder_content", "")
        text = title
        if content: text += "," + content
        self.set_output("tts_text", text)
        return NodeStatus.SUCCESS

class GenerateTTS(AsyncActionNode):
    def __init__(self, name="GenerateTTS"): super().__init__(name); self._t = None; self._ok = False
    def on_start(self) -> NodeStatus:
        text = self.get_input("tts_text", "reminder")
        self._ok = False
        self._t = threading.Thread(target=self._run, args=(text,), daemon=True)
        self._t.start()
        return NodeStatus.RUNNING
    def _run(self, text):
        try:
            safe = text.replace('"', "'")
            scr = "#!/bin/bash\nsource /opt/ros/humble/setup.bash\nros2 action send_goal /voice/speak robot_voice_bridge/action/Speak '{text: \"" + safe + "\"}' 2>/dev/null\n"
            with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
                f.write(scr)
                sp = f.name
            os.chmod(sp, 0o755)
            r = subprocess.run(["timeout", "30", sp], timeout=35, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.unlink(sp)
            self._ok = (r.returncode == 0)
        except Exception as e:
            print("[TTS] " + str(e))
            self._ok = False
    def on_tick(self) -> NodeStatus:
        if self._t and self._t.is_alive(): return NodeStatus.RUNNING
        return NodeStatus.SUCCESS if self._ok else NodeStatus.FAILURE
    def on_halt(self): self._ok = False

class PlaySpeaker(ActionNode):
    def __init__(self, name="PlaySpeaker"): super().__init__(name)
    def execute(self) -> NodeStatus: return NodeStatus.SUCCESS

class SavePersistence(ActionNode):
    def __init__(self, name="SavePersistence"): super().__init__(name)
    def execute(self) -> NodeStatus:
        rid = self.get_input("reminder_id", "r"+str(int(time.time())))
        d = self.get_input("data_dir", "board_data")
        os.makedirs(d, exist_ok=True)
        r = {"id": rid, "title": self.get_input("reminder_title",""), "content": self.get_input("reminder_content",""),
             "trigger_time": self.get_input("reminder_trigger_time",""), "is_repeating": self.get_input("reminder_is_repeating",False),
             "repeat_type": self.get_input("reminder_repeat_type","none"), "status": self.get_input("reminder_status","played"),
             "executed_at": datetime.now().isoformat()}
        p = os.path.join(d, rid+".json")
        with open(p+".tmp","w") as f: json.dump(r,f,ensure_ascii=False,indent=2)
        os.replace(p+".tmp", p)
        return NodeStatus.SUCCESS

class PublishStatus(ActionNode):
    def __init__(self, name="PublishStatus"): super().__init__(name)
    def execute(self) -> NodeStatus: return NodeStatus.SUCCESS