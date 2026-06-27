import re
src = open('/home/cat/reminder_bt/reminder_nodes.py').read()
old = 'def _run(self, text):'
m = re.search(r'def _run.*?(?=\n    def on_tick)', src, re.DOTALL)
if m:
    new = 'def _run(self, text):' + chr(10) + '        try:' + chr(10) + '            import tempfile' + chr(10) + '            safe = text.replace(chr(39), chr(34))' + chr(10) + '            scr = chr(35) + chr(33) + chr(47) + chr(98) + chr(105) + chr(110) + chr(47) + chr(98) + chr(97) + chr(115) + chr(104) + chr(10) + chr(115) + chr(111) + chr(117) + chr(114) + chr(99) + chr(101) + chr(32) + chr(47) + chr(111) + chr(112) + chr(116) + chr(47) + chr(114) + chr(111) + chr(115) + chr(47) + chr(104) + chr(117) + chr(109) + chr(98) + chr(108) + chr(101) + chr(47) + chr(115) + chr(101) + chr(116) + chr(117) + chr(112) + chr(46) + chr(98) + chr(97) + chr(115) + chr(104) + chr(10) + chr(114) + chr(111) + chr(115) + chr(50) + chr(32) + chr(97) + chr(99) + chr(116) + chr(105) + chr(111) + chr(110) + chr(32) + chr(115) + chr(101) + chr(110) + chr(100) + chr(95) + chr(103) + chr(111) + chr(97) + chr(108) + chr(32) + chr(47) + chr(118) + chr(111) + chr(105) + chr(99) + chr(101) + chr(47) + chr(115) + chr(112) + chr(101) + chr(97) + chr(107) + chr(32) + chr(114) + chr(111) + chr(98) + chr(111) + chr(116) + chr(95) + chr(118) + chr(111) + chr(105) + chr(99) + chr(101) + chr(95) + chr(98) + chr(114) + chr(105) + chr(100) + chr(103) + chr(101) + chr(47) + chr(97) + chr(99) + chr(116) + chr(105) + chr(111) + chr(110) + chr(47) + chr(83) + chr(112) + chr(101) + chr(97) + chr(107) + chr(32) + chr(39) + chr(123) + chr(116) + chr(101) + chr(120) + chr(116) + chr(58) + chr(32) + chr(34) + chr(39) + chr(43) + chr(115) + chr(97) + chr(102) + chr(101) + chr(43) + chr(39) + chr(34) + chr(125) + chr(39) + chr(39) + chr(32) + chr(50) + chr(62) + chr(47) + chr(100) + chr(101) + chr(118) + chr(47) + chr(110) + chr(117) + chr(108) + chr(108) + chr(10)
    new += '            with tempfile.NamedTemporaryFile(mode=chr(34)+chr(119)+chr(34), suffix=chr(34)+chr(46)+chr(115)+chr(104)+chr(34), delete=False) as f:' + chr(10)
    new += '                f.write(scr)' + chr(10) + '                sp = f.name' + chr(10)
    new += '            os.chmod(sp, 0o755)' + chr(10)
    new += '            r = subprocess.run([chr(39)+chr(116)+chr(105)+chr(109)+chr(101)+chr(111)+chr(117)+chr(116)+chr(39), chr(39)+chr(51)+chr(48)+chr(39), sp], timeout=35, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)' + chr(10)
    new += '            os.unlink(sp)' + chr(10)
    new += '            self._ok = (r.returncode == 0)' + chr(10)
    new += '        except Exception as e:' + chr(10) + '            print(chr(34)+chr(91)+chr(84)+chr(84)+chr(83)+chr(93)+chr(34)+chr(43)+chr(115)+chr(116)+chr(114)+chr(40)+chr(101)+chr(41)+chr(34))' + chr(10) + '            self._ok = False' + chr(10)
    src = src[:m.start()] + new + src[m.end():]
    open('/home/cat/reminder_bt/reminder_nodes.py','w').write(src)
    print('PATCHED')
else:
    print('NOT FOUND')