from world import WorldApi
import time


class Planner:

    def __init__(self):
        api = WorldApi()

        try:
            i = 0
            while True:
                print 40*"-"
                if api.getMyPosition() is not None:
                    print "My Position: ", api.getMyPosition()
                    print "My Angle: ", api.getMyOrientation()[1]
                else :    
                    print "My Position: ", api.getMyPosition()

                if api.getAllyPosition() is not None:    
                    print "Friend Position: ", api.getAllyPosition()
                    print "Friend Angle: ", api.getAllyOrientation()[1]
                else:
                    print "Friend Position: ", api.getAllyPosition()

                if api.getEnemyPositions()[0] is not None:
                    print "Enemy_0 Position: ", api.getEnemyPositions()[0]
                    print "Enemy_0 Angle: ", api.getEnemyOrientation()[0][1]
                else:
                    print "Enemy_0 Position: ", api.getEnemyPositions()[0]

                if api.getEnemyPositions()[1] is not None:
                    print "Enemy_0 Position: ", api.getEnemyPositions()[1]
                    print "Enemy_0 Angle: ", api.getEnemyOrientation()[1][1]
                else:
                    print "Enemy_0 Position: ", api.getEnemyPositions()[1]    

                print "Ball Center: ", api.getBallCenter()
                time.sleep(3)
        finally:
        # This needs to be run on both a clean or unclean exit. otherwise your threads won't close gracefully
            api.close()

if __name__ == "__main__":
    Planner()
