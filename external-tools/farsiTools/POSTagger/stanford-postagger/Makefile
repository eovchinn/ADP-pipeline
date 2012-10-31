# This is a rudimentary Makefile for rebuilding the POS tagger distribution.
# We actually use ant (q.v.) or a Java IDE.

JAVAC = javac
JAVAFLAGS = -O -d classes -encoding utf-8

postagger:
	mkdir -p classes
	$(JAVAC) -classpath CLASSPATH $(JAVAFLAGS) src/edu/stanford/nlp/*/*.java src/edu/stanford/nlp/*/*/*.java src/edu/stanford/nlp/*/*/*/*.java
	cd classes ; jar -cfm ../stanford-postagger-`date +%Y-%m-%d`.jar ../src/edu/stanford/nlp/tagger/maxent/documentation/postagger-manifest.txt edu ; cd ..
	cp stanford-postagger-`date +%Y-%m-%d`.jar stanford-postagger.jar



