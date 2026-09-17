# Head Server Configs
# A Config For Head Server

# Skins Server Configs
# Here You Can Config Skin Servers!
# Placeholders: {username}

# For Default... The Direct URL Are Supported
# But If You Want Mojang API Enter "mojang" As Default Setting
# Because For Mojang Players We Need To Request For UUID First
# Also "bedrock" Will Mean To Bedrock Skin
default = "mojang"

# mojang And bedrock Also Work Inside Here Too
# If You Need Skin System That Require Logics (Get UUID From Name -> Texture ID -> API -> Bra Bra Bra)
# You Will Need To Fork This Project
fallbacks = [
    "http://skinsystem.ely.by/skins/{username}.png",
    "https://auth.tlauncher.org/skin/fileservice/skins/skin_{username}.png",
    "bedrock"
]

# Skin Mode
# How Skin Will Reply To Client
# Options (Don't Care About Cases)
# [SOON] head: Return Player Face
# head-1-8: Return 1.8 Style Of Player Face (No Layer 2)
# [SOON] head-3d: Return Player 3D Head (Like Skull In Minecraft That Turn Right)
# [SOON] head-3d-l: Like head-3d But The Resault Turn Left
# Can Be Override By ?mode= Args
default_skin_mode = "HEAD-1-8"

# Bedrock Players Usually Have Prefix (Floodgate)
# If This Prefix Was Found We Will Immediately Throw The Name To Geyser First
# If You Running Pure Bedrock Server Leave This Blank
bedrock_prefix = "."

# Some Skin API Might Need User Agent... This Is Default One
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"

# Where WebServer Will Bind On?
host = "0.0.0.0"
port = 7500