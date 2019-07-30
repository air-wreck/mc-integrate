# the regular readme2tex stuff doesn't seem to work that robustly
for file in svgs/*.svg; do
  convert $file "${file%.svg}.png"
done
python3 -m readme2tex --output README.md INPUT.md --nocdn --branch master --pngtrick

