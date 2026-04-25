
#!/bin/bash

for i in {1..10}
do
   echo "Run $i/10"
   python3 -m src.baseline_counselor_agent_demo --counselor-config-path src/configs/llama3-8b_counselor_config.yaml --conversation-history-dir llama3-8b
done
