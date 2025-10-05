## System Setup

### NAO Robot Setup

1. Follow this [Documentation](http://doc.aldebaran.com/2-8/family/nao_user_guide/index.html) to `Turn On` your NAO robot.

2. Create a conda environment using `python 2.7`. Nao python SDK isn't compatible with other python versions. Install necessary packages in the `nao` environment

    ```
    conda create -n nao python=2.7
    conda activate nao
    pip install -r nao_requirements.txt
    ```

3. Download NaoQi Python SDK from: https://www.aldebaran.com/en/support/nao-6/downloads-softwares. Rename the SDK with a short name -- e.g. `python-sdk`. Check the following image for `ubuntu` system.

![NAOQi Install](../project_images/nao.png)

4. Set the following `path-variables` in the `nao` environment to install NaoQi. First, activate the `nao` environment and then run the following commands in the terminal one by one.

    ```
    export PYTHONPATH=${PYTHONPATH}: /<path-to-python-sdk>/lib/python2.7/site-packages 
    export DYLD_LIBRARY_PATH=${DYLD_LIBRARY_PATH}: /<path-to-python-sdk>/lib
    export QI_SDK_PREFIX= /<path-to-python-sdk>/
    ```

### Camera Setup

1. Creative shape design task requires a camera. Use an external camera and connect that with the system computer.

2. Set `camera_id` in the `task_1_ui` code.


### Feedback Environment Setup

1. Create a conda environment using `python 3.x`.

    ```
    conda create -n feedback python=3.10
    conda activate feedback
    ```
2. Install necessary packages in the `feedback` environment

    ```
    pip install -r feedback_requirements.txt
    ```


### System Test
1. To test whether the nao robot is working fine, activate the `nao` conda environment and then run `nao_client.py`. Before that update your nao `robot_ip` in the code.
    ```
    conda activate nao
    python nao_client.py
    ```
    Then activate the `feedback` environment in a different terminal and run the `test_nao.py`.
    
    ```
    conda activate feedback
    python test_nao.py
    ```
2. To test the speaker (voice-agent) connect it with the system computer and then run the `test_gtts.py`. 
    ```
    conda activate feedback
    python test_gtts.py


## Quickstart
1. Activate the two conda environments `nao`, `feedback` in two different terminals.

2. Before starting the session, make sure the nao robot (robot-agent) and the speaker (voice agent) is connected and wokring. In `nao` terminal run `nao_client.py`.
    ```
    python nao_client.py
    ```

3. For the creative shape design task connect a camera with the system computer and run the following command in `feedback` terminal. Select different `set_number` for different question set.
    ```
    python main.py --task_id task_1 --set_number 1

    ```

4. For the error detection task run the following command in `feedback` terminal. Select different `set_number` for different question set.
    ```
    python main.py --task_id task_2 --set_number 1

    ```