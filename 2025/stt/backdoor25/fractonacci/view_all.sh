#!/bin/bash
# View all important images
echo "Opening LSB visualizations..."
eog red_lsb_small.png &
sleep 2
eog interesting_tile_1_2500_2500.png &
sleep 2  
eog interesting_tile_2_2500_3000.png &
sleep 2
eog montage_tiles.png &
echo "Check the opened images for the flag!"
