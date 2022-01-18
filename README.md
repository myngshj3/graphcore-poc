# GraphCore
Graph and its attributes dynamic manipulation program for simulation !

[Introduction]

GraphCore is aiming to model the discrete component system and continuous physically performing system, simulate them, and visualize simulation result.
It was originally planned in 2019 and its draft was presented in the papers of APRIS2019 and FOSE2019.
GraphCore is consist in the following modules:

  o Modeler - modeling discrete component system in which any component is input as node and any relation between arbitrary two components is input as directed edge.
  
  o Solver - simulating model with computation based on attributes of model.
  
  o Visualizer - visualizing simulation result.

[Key Features]

Modeler:

  o Easy to model - easy to input without error and extra learning.
  
  o Custmizable component - most target discrete system can be modeled by customizing setting files.
  
  o Model-checker: real-time model-checking for input model.
  
  o MDI - multi-document interface support.

Solver:

  o Real-time computation - immediate computing when model changed.
  
  o Solver support - several solver are enabled to opt.
  
Visualizer:

  o Animation - continuous system or discrete event animation
  
  o CAE features - some CAE features employed.

[Current Achievements]

An application is opened as GraphCore application suite. Current supports are the following points:

  o Input, edit, save and load models.
  
  o Custmize component properties according to the user purposes.
  
  o Basic solver is implemented and it supports basic dataflow model. See graphcore-examples repository.

  o Fundamental visualizer is implemented and it shows component attribute's transition on simulated time series.
  
  o Script which manipulates graph, components and their attributes is implementd.
  
  o Script is also enabled to operate solver and post data.
  
  o Model constraints module is been implemented.
