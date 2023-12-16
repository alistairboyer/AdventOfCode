Advent of Code 2023
===================

  The Advent of Code sets a new coding challenge every day on the lead up to Christmas. 
  https://adventofcode.com/2023

  I was a bit late to the party but here are some random solutions to the 2023 challenge using python.

  My favourite ouput so far was from Day 10!
  ![Pipe maze output from Advent of Code 2023 Day 10](Day10.png)

                                                                                                                                            
Day 16
======
  There is another christmas maze, this time with light paths and mirrors.

  It is straightforwards to set up the maze and iteritively follow the light path. 
  The challenge is reminiscent of the pipes network on day 10 and 
    managed to repurpose a lot of setup and iteration code from that challenge.
  The key twist is that that there are beam splitters so each step can make multiple new beams.
  Additionally, the light can bounce forever between mirrors.
    
  To solve the problem I stepped through the maze one step at a time,
    logging each step and direction of a journal numpy.array.
  The journal also allowed tracking of any repeated light paths to avoid duplication or infinite loops.
  Using 1 bit per direction allowed for easy checking and combination, e.g. N = 1, W = 8 so NW = N | W = 9.

  Part two could have been a big one but the answer was revealed by brute force in only a few seconds.
  If the maze was bigger, or the challenge more complex an speedup could be achieved by caching
  light paths because brute force would have sent that poor reindeer all over the lava production facility
  with light repeating multiple times.
  


  
  
