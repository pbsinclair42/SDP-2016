import numpy as np

# color_range['COLOR_NAME'] = ( LOWER_TRESHOLD, UPPER_TRESHOLD )

color_range = {}
# pitch0 (D.304) ghost.name = aharacle/PC1 works the same on kilmore/PC3 
color_range['aharacle']['white'] = ( np.array([1, 0, 100]), np.array([36, 255, 255]) )
color_range['aharacle']['blue'] = ( np.array([95, 110, 110]), np.array([120, 255, 255]) )
# not 100% accurate bright_blue (depends on lightning)
color_range['aharacle']['bright_blue'] = ( np.array([80, 90, 110]), np.array([100, 255, 255]) )
color_range['aharacle']['pink'] = ( np.array([140, 120, 120]), np.array([170, 255, 255]) )
color_range['aharacle']['red'] = ( np.array([0, 170, 170]), np.array([4, 255, 255]) )
color_range['aharacle']['maroon'] = ( np.array([176, 170, 170]), np.array([180, 255, 255]) )
color_range['aharacle']['green'] = ( np.array([50, 190, 190]), np.array([55, 255, 255]) )
color_range['aharacle']['bright_green'] = ( np.array([60, 110, 110]), np.array([75, 255, 255]) )
color_range['aharacle']['yellow'] = ( np.array([27, 130, 130]), np.array([40, 255, 255]) )



