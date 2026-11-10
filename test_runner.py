import sys
import pathlib

repo_dir = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(repo_dir))

import maya_bridge

print("Pinging Maya...")
if not maya_bridge.ping():
    print("Maya bridge not responding!")
    sys.exit(1)

print("Maya bridge is alive! Running create_test_rig('bouncing_ball')...")
result = maya_bridge.run_file(
    str(repo_dir / "squash_stretch.py"),
    "res = create_test_rig('bouncing_ball'); print('SUCCESS:', res['type'])"
)
print("Bridge response:", result)
