
#!/bin/bash

for i in {1..10}
do
   echo "Run $i/10"
   python3 -m src.baseline_counselor_agent_demo
done
