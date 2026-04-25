
#!/bin/bash

for i in {1..10}
do
   echo "Run $i/10"
   python3 -m src.baseline_counselor_agent_demo --counselor-config-path src/configs/gpt-4o_counselor_config.yaml --conversation-history-dir gpt-4o
done
