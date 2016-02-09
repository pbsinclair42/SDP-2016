import numpy as np

# color_range[('COMPUTER_NAME, COLOR_NAME')] = ( LOWER_TRESHOLD, UPPER_TRESHOLD )
color_range = {}
# pitch0 (D.304) ghost.name = aharacle/PC1 works the same on kilmore/PC3 
color_range[('aharacle','white')] = ( np.array([1, 0, 100]), np.array([36, 255, 255]) )
color_range[('aharacle','blue')] = ( np.array([95, 110, 110]), np.array([125, 255, 255]) )
color_range[('aharacle','bright_blue')] = ( np.array([80, 110, 110]), np.array([105, 255, 255]) )
color_range[('aharacle','pink')] = ( np.array([150, 110, 110]), np.array([175, 255, 255]) )
color_range[('aharacle','red')] = ( np.array([0, 175, 175]), np.array([3, 255, 255]) )
color_range[('aharacle','maroon')] = ( np.array([177, 175, 175]), np.array([180, 255, 255]) )
color_range[('aharacle','green')] = ( np.array([50, 190, 190]), np.array([55, 255, 255]) )
color_range[('aharacle','bright_green')] = ( np.array([52, 190, 190]), np.array([60, 255, 255]) )
color_range[('aharacle','yellow')] = ( np.array([25, 145, 145]), np.array([40, 255, 255]) )

# pitch0 (D.304) kilmore/PC3
color_range[('kilmore','white')] = ( np.array([1, 0, 100]), np.array([36, 255, 255]) )
color_range[('kilmore','blue')] = ( np.array([105, 110, 110]), np.array([125, 255, 255]) )
color_range[('kilmore','bright_blue')] = ( np.array([65, 120, 120]), np.array([100, 255, 255]) )
color_range[('kilmore','pink')] = ( np.array([140, 110, 110]), np.array([175, 255, 255]) )
color_range[('kilmore','red')] = ( np.array([0, 175, 175]), np.array([4, 255, 255]) )
color_range[('kilmore','maroon')] = ( np.array([176, 175, 175]), np.array([180, 255, 255]) )
color_range[('kilmore','green')] = ( np.array([50, 190, 190]), np.array([55, 255, 255]) )
color_range[('kilmore','bright_green')] = ( np.array([52, 190, 190]), np.array([60, 255, 255]) )
color_range[('kilmore','yellow')] = ( np.array([25, 145, 145]), np.array([40, 255, 255]) )

# pitch0 (D.303) ghost.name = knapdale/PC4
color_range[('knapdale','white')] = ( np.array([1, 0, 100]), np.array([36, 255, 255]) )
color_range[('knapdale','blue')] = ( np.array([95, 110, 110]), np.array([120, 255, 255]) )
color_range[('knapdale','bright_blue')] = ( np.array([80, 90, 110]), np.array([100, 255, 255]) )
color_range[('knapdale','pink')] = ( np.array([140, 110, 110]), np.array([175, 255, 255]) )
color_range[('knapdale','red')] = ( np.array([0, 170, 170]), np.array([4, 255, 255]) )
color_range[('knapdale','maroon')] = ( np.array([176, 170, 170]), np.array([180, 255, 255]) )
color_range[('knapdale','green')] = ( np.array([50, 190, 190]), np.array([55, 255, 255]) )
color_range[('knapdale','bright_green')] = ( np.array([60, 110, 110]), np.array([75, 255, 255]) )
color_range[('knapdale','yellow')] = ( np.array([30, 150, 150]), np.array([40, 255, 255]) )

# SDP main lab ghost.name = amble
color_range[('amble','white')] = ( np.array([1, 0, 100]), np.array([36, 255, 255]) )
color_range[('amble','blue')] = ( np.array([105, 140, 140]), np.array([120, 255, 255]) )
color_range[('amble','bright_blue')] = ( np.array([80, 100, 100]), np.array([100, 255, 255]) )
color_range[('amble','pink')] = ( np.array([150, 120, 120]), np.array([170, 255, 255]) )
color_range[('amble','red')] = ( np.array([0, 190, 190]), np.array([4, 255, 255]) )
color_range[('amble','maroon')] = ( np.array([176, 190, 190]), np.array([180, 255, 255]) )
color_range[('amble','green')] = ( np.array([60, 110, 110]), np.array([75, 255, 255]) )
color_range[('amble','bright_green')] = ( np.array([51, 200, 200]), np.array([53, 255, 255]) )
color_range[('amble','yellow')] = ( np.array([20, 130, 130]), np.array([40, 255, 255]) )
