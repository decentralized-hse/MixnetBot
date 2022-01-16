import time

from DesktopClient.MixnetClient import MixnetClient

app = MixnetClient()
app.send(app.key_manager.pk_packed, f"RRRRRR")
# for i in range(50):
#     app.send(app.key_manager.pk_packed, f"___{i}")

time.sleep(3)
senders, messages = app.update_manager.get_updates(all_messages=True)

print(messages)
