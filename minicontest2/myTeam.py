# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import nearestPoint
eaten=0
#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class AgentKing(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.width=gameState.data.layout.width
    self.initFood = self.getFood(gameState).asList()
    #print(len(self.initFood))
    '''
    Your initialization code goes here, if you need any.
    '''



  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    """
       Picks among the actions with the highest Q(s,a).
       """
    #actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
    foodL=self.getFood(gameState).asList()
    foodLeft = len(foodL)
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]





    if foodLeft <= 2:
        bestDist = 9999
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            pos2 = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(self.start, pos2)
            if dist < bestDist:
                bestAction = action
                bestDist = dist
        return bestAction


    chosenAction=random.choice(bestActions)
    successor = self.getSuccessor(gameState, chosenAction)
    global eaten
    if successor.getAgentPosition(self.index) in foodL:
        eaten += 1
    return chosenAction


  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class OffensiveReflexAgent(AgentKing):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['numoffood'] = -len(foodList)
    features['successorScore']=self.getScore(successor)
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

    #print(enemies)
    attackerList = [a for a in enemies if a.isPacman == False and a.getPosition() != None]
    capsule = self.getCapsules(successor)
    
    # Compute distance to the nearest food
    myPos = successor.getAgentState(self.index).getPosition()
    minEnemy = 5
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
      #if len(attackerList)>0:
        #minEnemy = min([self.getMazeDistance(myPos, enemy.getPosition()) for enemy in attackerList if enemy.scaredTimer == 0 ])

      for enemy in attackerList:
          if enemy.scaredTimer == 0:
              dis=self.getMazeDistance(myPos, enemy.getPosition())
              #print(dis)
              if dis<minEnemy:
                  minEnemy=dis

    features['distanceToGhost']=minEnemy
    minCapsule=0
    if(len(capsule)) > 0:
      minCapsule = min([self.getMazeDistance(myPos, cap) for cap in capsule])
    features['capsuledist'] = minCapsule
    features['capsulelen']=-len(capsule)

    actions = successor.getLegalActions(self.index)
    #print(actions)
    numofact = len(actions)
    if numofact > 3 or features['distanceToGhost'] ==5:
        numofact = 3
    #print(numofact)
    features['numofact'] = numofact

    #safex=0
    #dis2safe=0
    global eaten
    if self.red:
        safex=self.width/2 - 1
        x,y=myPos
        dis2safe=x-safex
        if dis2safe<0:
            eaten=0
            dis2safe=0
    else:
        safex = self.width / 2
        x, y = myPos
        dis2safe = safex-x
        if dis2safe < 0:
            eaten=0
            dis2safe = 0
    features['dis2safe'] = dis2safe
    huntscore=0
    for ghost in enemies:
        if ghost.scaredTimer > 0:
            ghostPos = ghost.getPosition()
            dis =self.getMazeDistance(myPos, ghostPos)
            if dis < 5:
                huntscore += 10
            if dis < 2:
                huntscore += 100
            if dis < features['distanceToFood']:
                features['distanceToFood'] = dis
    features['huntscore']=huntscore
    return features

  def getWeights(self, gameState, action):
    global eaten
    #print(eaten)
    if eaten<3:
        return {'numoffood': 100,'successorScore':1,'numofact':100,'distanceToFood': -10, 'distanceToGhost': 10, 'capsuledist': -1,'capsulelen': 100,\
                'huntscore':10,'dis2safe':-1}
    else:
        return {'numoffood': 0, 'successorScore': 1, 'numofact': 100, 'distanceToFood': 0, 'distanceToGhost': 100,
                'capsuledist': 1, 'capsulelen': 1, \
                'huntscore': 10, 'dis2safe': -100}
class DefensiveReflexAgent(AgentKing):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
