# the regular readme2tex stuff doesn't seem to work that robustly
for file in svgs/*.svg; do
  convert -density 300 $file "${file%.svg}.png"
done
python3 -m readme2tex --output README.md INPUT.md --nocdn --branch master --pngtrick

