# SDP-2016 
# Team B 
# Group 3-4

Vision stuff


## Running

    cd vision && python robot_tracking.py

The above will start a server, and get it broadcasting the relevant info (robot position, orientation) from port (default 5555)
you can test that the client is working with the simple `python client.py`. This will connect to the port, and print the output.

Useful for callibration:
- colorsHSV.py: to change color internal representation
- camera.py: to change camera brightness, hue, etc
- scripts/get_camera_configuration.py is used to undistort the pitch image for the specific pitc
- test/gui_point_finder can be helpful for finding image correct transformations if the pitch image is incorrectly undistorted

ALSO NOTE:
camera settings are very dependent pitch settings:

*I think that*
3.D03 represented as 1
3.D04 represented as 0

This ALWAYS needs to be configured in a few files when you know which pitch is to be used.
Depending on the pitch settings the camera feed is undistorted in a very different way.

## Planning Wrapper

A simple wrapper around the Vision system has been included in the `planningwrapper` directory.
It contains a `WorldApi` object, which handles all of the polling from the vision server.

please note that you _need_ to call `api.close()` before you exit your program (even if your program crashes!).
This is covered in more detail in the *sample_planner.py* file.


# TODO

- allow command-line switch to set port
