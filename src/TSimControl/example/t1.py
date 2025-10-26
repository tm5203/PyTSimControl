import time
import sys
import os
import logging

if __name__ == '__main__':
    t = int(sys.argv[1]) if len(sys.argv) >= 2 else 5
    pid = os.getpid()
    logger = logging.getLogger('t1')
    logHandler = logging.StreamHandler(sys.stdout)
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    
    for c in range(t):
        logger.info('t1 %d : %s %d / %d' , pid, sys.argv[2], c + 1, t)
        time.sleep(1)
    sys.exit(0)
