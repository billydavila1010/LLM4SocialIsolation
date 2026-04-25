
#!/bin/bash

for i in {1..10}
do
   echo "Run $i/10"
   python3 -m src.baseline_counselor_agent_demo --counselor-config-path src/configs/Mixtral-8x22B.yaml --conversation-history-dir Mixtral-8x22B
done
