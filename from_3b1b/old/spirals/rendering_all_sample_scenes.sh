#!/bin/bash

# Create folders
rm -rf /tmp/assets
mkdir -p /tmp/assets/raster_images
mkdir -p /tmp/assets/svg_images/assets

# Emulate missing PiCreature
cp $PWD/manimlib/files/*.svg /tmp/assets/
cp $PWD/manimlib/files/*.svg /tmp/assets/svg_images
cp $PWD/manimlib/files/*.svg /tmp/assets/svg_images/assets
SVGS="raise_right_hand thinking raise_right_hand confused pondering maybe angry happy hooray hesitant sassy erm horrified surprised guilty raise_left_hand tired"
for SVGNAME in $SVGS; do
    ln -fs ./PiCreatures_plain.svg /tmp/assets/svg_images/assets/PiCreatures_${SVGNAME}.svg
done

# PrimeSpiral image replacement
curl -o /tmp/assets/raster_images/PrimeSpiral.png https://upload.wikimedia.org/wikipedia/commons/b/b0/Ulam_Spiral_Divisors_100000.png

# Dirichlet image replacement
curl -o /tmp/assets/raster_images/Dirichlet.jpg https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Dirichlet.jpg/220px-Dirichlet.jpg

# Lightbulb image replacement
curl -o /tmp/assets/svg_images/lightbulb.svg https://upload.wikimedia.org/wikipedia/commons/a/a3/Light_bulb_%28yellow%29_icon.svg

# Emulate sound
docker run --rm -it -v $PWD:/tmp/input -v /tmp/assets:/tmp/input/assets -v $PWD/media:/tmp/output -w /tmp/input --entrypoint '' eulertour/manim bash -c "sox -n -r 8000 /tmp/input/pen_click.wav synth 3 sine 333"

# Generate primes
docker run --rm -it -v $PWD:/tmp/input -v /tmp/assets:/tmp/input/assets -v $PWD/media:/tmp/output -w /tmp/input --entrypoint '' eulertour/manim bash -c "python from_3b1b/old/spirals/generate_primes.py -n 100000 -f /tmp/input/assets/primes_1e5.json;  python from_3b1b/old/spirals/generate_primes.py -n 1000000 -f /tmp/input/assets/primes_1e6.json; python from_3b1b/old/spirals/generate_primes.py -n 10000000 -f /tmp/input/assets/primes_1e7.json"

# Generate scenes
docker run --rm -it -v $PWD:/tmp/input -v /tmp/assets:/tmp/input/assets:ro -v $PWD/media:/tmp/output -w /tmp/input --entrypoint '' eulertour/manim python -m manim from_3b1b/old/spirals/spirals.py -al
