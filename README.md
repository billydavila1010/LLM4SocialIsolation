## Retrieval-Augmented LLM Agents for the Memory Reactivation of Social Isolated Groups

### Codebase Structure
```shell
LLM4SocialIsolation
├── README.md
├── assets
├── requirements.txt
├── scripts
│   └── run_demo.sh
└── src
    ├── agents
    │   ├── __init__.py
    │   ├── chat_llm.py
    │   ├── context.py
    │   ├── counselor_agent.py
    │   └── patient_agent.py
    ├── configs
    │   ├── counselor_config.yaml
    │   └── patient_config.yaml
    ├── conversation.py
    ├── demo.py
    ├── eval
    │   └── __init__.py
    ├── memory
    │   └── __init__.py
    ├── prompts
    │   ├── __init__.py
    │   ├── counselor_prompts.py
    │   └── patient_prompts.py
    └── utils
        ├── __init__.py
        ├── chat_llm.py
        ├── emotion_detector.py
        └── utils.py
```
### Notes:
1. Please always remember to check updates from the `main` branch (`git status` or `git pull origin main`). 
2. When submitting your code, please `first push to your personal branch` and then create a `pull request` to the `main` branch.
3. Please try to **parameterize all the variables** and try avoiding hardcode any variables
4. Please consider the `Python PEP8 standard` when creating variable/function names. We will review the submitted code before merging them into the `main` branch.
5. Please save all the experimental results, e.g., conversation history/sessions, in `./experiments`.
6. Please save all the resources, e.g., autobiography in `./assets`.

### Environment
```shell
conda create -n <conda name> python=3.10
pip install -r requirements.txt
```

### Scripts
#### run demo
```shell
cd LLM4SocialIsolation

python -m src.demo \
--patient-config-path ./src/configs/patient_config.yaml \
--counselor-config-path ./src/configs/counselor_config.yaml \
--output-path ./experiments/test.json
```
or
```shell
cd LLM4SocialIsolation
sh scripts/run_demo.sh
```