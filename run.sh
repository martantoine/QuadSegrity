#!/bin/sh
rm leg_parametric.xml   
python main.py

unamestr=$(uname)
if [[ "$unamestr" == 'Linux' ]]; then
    ./mujoco/bin/simulate leg_parametric.xml
elif [[ "$unamestr" == 'Darwin' ]]; then
    open -n mujoco/MuJoCo.app --args $(pwd)/leg_parametric.xml
fi
