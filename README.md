Mouse-and-Cat game with Q-Learning.
===================================================

<b>QLearningMouse</b>  is a small cat-mouse-cheese game based on [Q-Learning](https://en.wikipedia.org/wiki/Q-learning). The original version is from [vmayoral](https://github.com/vmayoral): [basic_reinforcement_learning:tutorial1](https://github.com/vmayoral/basic_reinforcement_learning/tree/master/tutorial1), I resconstructed his code to make the game more configurable, and what different most is that I use breadth-first-search([BFS](https://en.wikipedia.org/wiki/Breadth-first_search)) when cat chasing the AI mouse, so it looks much more fierce :P 

### About the game
Cat chases the mouse always in the shortest path with BFS, however the mouse first does not know the danger of being eaten. It earns reward value of 50 when eating the cheese,  yet gaining reward value of -100 when dead.

### Algorithm  
The basic algorithm of Q-Learning is:  
```
Q(s, a) += alpha * (reward(s,a) + gamma * max(Q(s', a') - Q(s,a))
```
    
* ```alpha``` is the learning rate.
* ```gamma``` is the value of the future reward.
It use the best next choice of utility in later state to update the former state. 

Learn more about Q-Learning:  
- [The Markov Decision Problem : Value Iteration and Policy Iteration](http://ais.informatik.uni-freiburg.de/teaching/ss03/ams/DecisionProblems.pdf)  
- [ARTIFICIAL INTELLIGENCE FOUNDATIONS OF COMPUTATIONAL AGENTS : 11.3.3 Q-learning](http://artint.info/html/ArtInt_265.html)


### Example
Below we present a *mouse player* after **300 generations** of reinforcement learning:  
* blue is for mouse.
* black is for cat.
* orange is for cheese.

![](resources/snapshot1.gif)

After **330000 generations**:  

![](resources/snapshot2.gif)


### Reproduce it yourself

```bash
git clone https://github.com/fancoo/QLearningMouse
cd QLearningMouse
python greedyMouse.py
```
