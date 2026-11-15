#!/data/data/com.termux/files/usr/bin/bash
pkg update -y && pkg install python openssh -y
mkdir -p ~/ZERO-HACK
cp zero_hack.py ~/ZERO-HACK/
cat << 'INNER' > $PREFIX/bin/play
#!/data/data/com.termux/files/usr/bin/bash
[ "$1" == "-zero_hack" ] && python ~/ZERO-HACK/zero_hack.py "${@:2}" || echo "Usage: play -zero_hack"
INNER
chmod +x $PREFIX/bin/play
echo -e "\033[92m[+] ZERO->HACK Installed Successfully! Run: play -zero_hack\033[0m"
