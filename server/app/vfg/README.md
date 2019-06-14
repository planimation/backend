# Planning Visualisation - Visualsition File Generator

Here is the link to the document explaining the VFG component algorithms:
https://confluence.cis.unimelb.edu.au:8443/display/SWEN900132018PL/Predicate+Solver+Document

This python program takes the domain PDDL, problem PDDL and the animation profile to generate the Visualisation file for the Visualisor program.

## How to run the program
In the terminal, with python3 installed, run the following command and it will generate a file called visualisation.json in the root folder

```
python main.py [dommainfile] [problemfile] [animationprofile]

eg. python main.py domain_blocks.pddl problems/bw01.pdd animation_profile.json
```

## Versioning

2.0

## Limitations

### Planning domain API
The planning domain API could only solve the block problems that the total number of block is below 25, otherwise the API has high chance return timeout error

### Parser:
Current parser is general, it works well with the domain file and problem file we provided which use the following predicates


### Animation Profile
In sprint 2 the Animation Profile is create by ourself, it is written in Json

### Visualisation File Generator
The visualisation file generator works for block domain and grid domain at the moment.

## Authors
* **Team Planning Visualisation** - *Initial work* -

## Acknowledgments

* Planning domain API (http://solver.planning.domains/)
