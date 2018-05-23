
from repo.server_modules import Server,Handler


handler = Handler()
servver=Server('Totem',handler)
servver.start()


