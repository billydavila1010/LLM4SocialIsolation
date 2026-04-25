
#!/bin/bash

for i in {1..20}
do
   echo "Run $i/20"
  python3 -m src.demo --patient-config-path ./src/configs/catherine_helen_spence.yaml --conversation-history-dir ./experiments/no-vip
done
